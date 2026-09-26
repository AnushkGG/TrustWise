"""
TrustWise Web Frontend

Flask-based web interface for the TrustWise system.
Provides a user-friendly UI for submitting queries and viewing results.
"""

import json
import os
import sys
import secrets
from datetime import datetime
from pathlib import Path

# Ensure the project root is on sys.path so imports work when run from legacy/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule, execute_chunks
from agents import web_agent, research_agent
from cleaner import normalize_results
from trust import validate_structured_data
from storage import get_cached_trusted_items, save_trusted_items
from insights import generate_insights
from utils.config import Config
from utils.logger import setup_logger
from utils.retry import execute_with_retry

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
logger = setup_logger(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
    return response

# Store active execution state
execution_state = {
    "current_plan": None,
    "current_results": [],
    "is_running": False
}


@app.route('/')
def index():
    """Main page with query input form."""
    return render_template('index.html')


@app.route('/api/submit', methods=['POST'])
def submit_query():
    """
    API endpoint to submit a query and execute the pipeline.
    
    Returns:
        JSON with plan and execution results
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        logger.info(f"Web UI: Processing query: {query}")
        
        # Mark as running
        execution_state["is_running"] = True
        execution_state["current_results"] = []
        
        # Step 1: Generate Plan
        plan = generate_plan(query)
        execution_state["current_plan"] = plan

        # Step 1.5: Check local trusted DB cache first (Phase 6)
        if Config.ENABLE_DB_CACHE:
            cached_items = get_cached_trusted_items(
                query=query,
                min_items=Config.DB_CACHE_MIN_ITEMS,
                limit=8,
            )
            if cached_items:
                execution_state["is_running"] = False
                insights = generate_insights(cached_items, query=query)

                response = {
                    'success': True,
                    'plan': {
                        'goal': plan.get('goal'),
                        'domains': plan.get('domains'),
                        'time_range': plan.get('time_range'),
                        'sources': plan.get('sources'),
                        'total_tasks': len(plan.get('tasks', []))
                    },
                    'execution': {
                        'web_tasks': 0,
                        'paper_tasks': 0,
                        'total_results': 0,
                        'successful': 0,
                        'structured_items': len(cached_items),
                        'trusted_items': len(cached_items),
                        'db_inserted': 0,
                        'db_skipped': 0,
                        'cache_hit': True
                    },
                    'results': [],
                    'structured_data': cached_items,
                    'trusted_data': cached_items,
                    'insights': insights,
                    'trust_report': {
                        'validated_count': len(cached_items),
                        'trusted_count': len(cached_items),
                        'dropped_count': 0
                    }
                }

                logger.info("Web UI: Served query from trusted DB cache")
                return jsonify(response)
        
        # Step 2: Chunk Tasks
        chunks = chunk_tasks(plan)
        
        # Step 3 & 4: Schedule and Execute Chunks Concurrently
        results = execute_chunks(chunks)
        execution_state["current_results"] = results

        # Step 5: Clean and structure outputs (Phase 2)
        structured_data = normalize_results(results, query=query)

        # Step 6: Apply zero-trust validation (Phase 3)
        trust_report = validate_structured_data(structured_data, query=query)
        trusted_data = trust_report["trusted_items"]

        # Step 7: Persist trusted items (Phase 4)
        db_stats = {"inserted": 0, "skipped": 0}
        if Config.SAVE_TO_DB:
            db_stats = save_trusted_items(trusted_data, query=query)

        # Step 8: Generate insights from the best available data (Phase 5)
        insight_input = trusted_data if trusted_data else structured_data
        insights = generate_insights(insight_input, query=query)
        
        execution_state["is_running"] = False
        
        # Prepare response
        response = {
            'success': True,
            'plan': {
                'goal': plan.get('goal'),
                'domains': plan.get('domains'),
                'time_range': plan.get('time_range'),
                'sources': plan.get('sources'),
                'total_tasks': len(plan.get('tasks', []))
            },
            'execution': {
                'web_tasks': sum(1 for t in plan.get('tasks', []) if t.get('type') == 'web'),
                'paper_tasks': sum(1 for t in plan.get('tasks', []) if t.get('type') == 'paper'),
                'total_results': len(results),
                'successful': sum(1 for r in results if r.get('status') == 'success'),
                'structured_items': len(structured_data),
                'trusted_items': len(trusted_data),
                'db_inserted': db_stats['inserted'],
                'db_skipped': db_stats['skipped'],
                'cache_hit': False
            },
            'results': results,
            'structured_data': structured_data,
            'trusted_data': trusted_data,
            'insights': insights,
            'trust_report': {
                'validated_count': trust_report['validated_count'],
                'trusted_count': trust_report['trusted_count'],
                'dropped_count': trust_report['dropped_count']
            }
        }
        
        logger.info(f"Web UI: Query completed successfully")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Web UI: Query execution failed: {e}", exc_info=True)
        execution_state["is_running"] = False
        return jsonify({
            'success': False,
            'error': 'An internal error occurred while processing the query.'
        }), 500


@app.route('/api/plans')
def list_plans():
    """
    API endpoint to list all saved plans.
    
    Returns:
        JSON array of saved plans with metadata
    """
    try:
        plans_dir = Config.PLANS_DIR
        plan_files = sorted(plans_dir.glob('plan_*.json'), reverse=True)
        
        plans = []
        for plan_file in plan_files[:20]:  # Limit to 20 most recent
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                    plans.append({
                        'filename': plan_file.name,
                        'goal': plan_data.get('goal', 'N/A'),
                        'created_at': plan_data.get('_metadata', {}).get('created_at', 'Unknown'),
                        'query': plan_data.get('_metadata', {}).get('query', 'N/A'),
                        'tasks': len(plan_data.get('tasks', []))
                    })
            except Exception as e:
                logger.warning(f"Failed to read plan {plan_file}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'plans': plans
        })
        
    except Exception as e:
        logger.error(f"Failed to list plans: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list plans.'
        }), 500


@app.route('/api/plan/<filename>')
def get_plan(filename):
    """
    API endpoint to get a specific plan by filename.
    
    Args:
        filename: Name of the plan file
        
    Returns:
        JSON of the plan
    """
    try:
        # Security: prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        plan_file = (Config.PLANS_DIR / filename).resolve()
        
        # Verify the resolved path is still within PLANS_DIR
        plans_dir = Config.PLANS_DIR.resolve()
        try:
            plan_file.relative_to(plans_dir)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        if not plan_file.exists():
            return jsonify({
                'success': False,
                'error': 'Plan not found'
            }), 404
        
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        return jsonify({
            'success': True,
            'plan': plan_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get plan {filename}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve plan.'
        }), 500


@app.route('/api/status')
def get_status():
    """
    API endpoint to get system status.
    
    Returns:
        JSON with system configuration and status
    """
    try:
        gemini_configured = bool(Config.GEMINI_API_KEY)
        freellmapi_configured = bool(Config.FREELLMAPI_API_KEY)
        ollama_reachable = False
        try:
            import requests
            resp = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=2)
            ollama_reachable = resp.status_code == 200
        except Exception:
            pass

        if Config.LLM_PROVIDER == "both":
            has_api_key = gemini_configured or ollama_reachable
        elif Config.LLM_PROVIDER == "gemini":
            has_api_key = gemini_configured
        elif Config.LLM_PROVIDER == "ollama":
            has_api_key = ollama_reachable
        elif Config.LLM_PROVIDER == "freellmapi":
            has_api_key = freellmapi_configured
        else:
            has_api_key = False

        providers_available = []
        if gemini_configured:
            providers_available.append("gemini")
        if ollama_reachable:
            providers_available.append("ollama")
        if freellmapi_configured:
            providers_available.append("freellmapi")

        return jsonify({
            'success': True,
            'status': {
                'llm_provider': Config.LLM_PROVIDER,
                'llm_model': Config.LLM_MODEL,
                'has_api_key': has_api_key,
                'ollama_reachable': ollama_reachable,
                'gemini_configured': gemini_configured,
                'freellmapi_configured': freellmapi_configured,
                'providers_available': providers_available,
                'save_plans': Config.SAVE_PLANS,
                'save_raw_data': Config.SAVE_RAW_DATA,
                'save_structured_data': Config.SAVE_STRUCTURED_DATA,
                'save_trusted_data': Config.SAVE_TRUSTED_DATA,
                'save_to_db': Config.SAVE_TO_DB,
                'enable_db_cache': Config.ENABLE_DB_CACHE,
                'is_running': execution_state.get('is_running', False)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system status.'
        }), 500


@app.route('/api/raw-data')
def list_raw_data():
    """
    API endpoint to list raw data files.
    
    Returns:
        JSON array of raw data files
    """
    try:
        raw_dir = Config.RAW_DATA_DIR
        raw_files = sorted(raw_dir.glob('task_*.json'), reverse=True)
        
        files = []
        for raw_file in raw_files[:50]:  # Limit to 50 most recent
            try:
                stat = raw_file.stat()
                files.append({
                    'filename': raw_file.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to stat file {raw_file}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        logger.error(f"Failed to list raw data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list raw data.'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("TrustWise Web Interface")
    print("=" * 60)
    print(f"LLM Provider: {Config.LLM_PROVIDER}")
    print(f"LLM Model: {Config.LLM_MODEL}")
    
    if Config.LLM_PROVIDER == "ollama":
        print(f"Ollama URL: {Config.OLLAMA_BASE_URL}")
        try:
            import requests
            resp = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=2)
            if resp.status_code == 200:
                models = [m['name'] for m in resp.json().get('models', [])]
                print(f"[OK] Ollama is running - available models: {', '.join(models)}")
            else:
                print("[WARN] Ollama server responded but returned an error")
        except Exception:
            print("[WARN] Cannot connect to Ollama. Make sure 'ollama serve' is running")
    elif Config.LLM_PROVIDER == "freellmapi":
        print(f"FreeLLMAPI URL: {Config.FREELLMAPI_BASE_URL}")
        print(f"FreeLLMAPI Model: {Config.get_freellmapi_model()}")
        if Config.FREELLMAPI_API_KEY:
            print("[OK] FreeLLMAPI API key configured")
        else:
            print("[WARN] FREELLMAPI_API_KEY not set")
    else:
        try:
            Config.validate()
            print("[OK] Using real LLM API")
        except ValueError:
            print("[WARN] Using mock LLM responses (no API key configured)")
    
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host = os.getenv("HOST", "0.0.0.0")
    app.run(debug=debug_mode, host=host, port=5000)
