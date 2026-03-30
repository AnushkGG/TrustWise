# TrustWise Quick Start Guide

Get TrustWise up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Gemini API key or local Ollama server (optional — system works without using mock responses)

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# 1. Run setup script
python setup.py

# 2. Edit .env and add your API key (optional)
# Open .env in any text editor and replace:
# GEMINI_API_KEY=your_gemini_api_key_here

# 3. Run the system
python main.py
```

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 3. Edit .env and add your API key

# 4. Run the system
python main.py
```

## First Run

When you run `python main.py`, you'll see:

```
============================================================
TrustWise - Trust-First AI System (Phase 1)
============================================================

Enter your query:
```

Try entering:

```
Latest AI developments in healthcare
```

The system will:

1. ✅ Generate a structured execution plan
2. ✅ Break it into tasks
3. ✅ Route tasks to agents
4. ✅ Collect data from web and research sources
5. ✅ Save everything for audit trail

## Running Without API Key

The system works without API keys by using mock LLM responses. This is perfect for:

- Testing the architecture
- Understanding the flow
- Development without API costs

Just run `python main.py` and it will automatically use mock responses.

## Example Queries

Try these queries to see different aspects of the system:

1. **Web + Research Papers**:

   ```
   What are the latest developments in quantum computing?
   ```

2. **Healthcare Focus**:

   ```
   Find recent AI diagnostic tools and research papers
   ```

3. **Weekly Updates**:

   ```
   Weekly tech news on cybersecurity and AI
   ```

4. **Specific Domain**:
   ```
   Latest transformer model research in computer vision
   ```

## Demo Mode

Run the demo script to see multiple queries automatically:

```bash
python demo.py
```

This runs 4 example queries and shows you the complete flow without manual input.

## Understanding the Output

### Console Output

```
🔄 Generating execution plan...

============================================================
📋 GENERATED PLAN
============================================================
Goal: Track latest AI developments in healthcare
Domains: artificial_intelligence, healthcare
Time Range: latest
Sources: web, research_papers
Tasks: 4
============================================================

📊 Scheduled 2 web tasks and 2 research tasks

🌐 Executing Web Tasks...
   ✓ task_web_1: success
   ✓ task_web_2: success

📚 Executing Research Tasks...
   ✓ task_paper_1: success
   ✓ task_paper_2: success

============================================================
✅ EXECUTION COMPLETE
============================================================
Tasks completed: 4/4
Raw data saved to: data\raw
Plan saved to: data\plans
```

### Generated Files

After running, check these folders:

1. **`data/plans/`** - Execution plans (JSON)
   - Auditable record of what was requested
   - Reproducible execution plans

2. **`data/raw/`** - Raw agent outputs (JSON)
   - Web scraping results
   - Research paper metadata

## Configuration

Edit `.env` to customize:

```env
# Use Gemini (cloud) or Ollama (local)
LLM_PROVIDER=gemini

# Your Gemini API key
GEMINI_API_KEY=your_key_here

# Or use Ollama (local):
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# LLM_MODEL=llama3

# Model selection
LLM_MODEL=gemini-2.0-flash

# How many papers to fetch
ARXIV_MAX_RESULTS=5

# Save outputs?
SAVE_PLANS=true
SAVE_RAW_DATA=true
```

## Troubleshooting

### "GEMINI_API_KEY is required"

**Solution**: This is just a warning. The system will use mock responses. To use real LLM:

1. Get an API key from https://aistudio.google.com/apikey
2. Add it to `.env`: `GEMINI_API_KEY=your-actual-key`

### "Import Error: google-generativeai not installed"

**Solution**: Install dependencies:

```bash
pip install -r requirements.txt
```

### "No data collected from any source"

**Solution**: This is normal in Phase 1 when:

- Websites block scraping
- Network issues
- Rate limiting

The system will continue and mark tasks as "partial" status.

### "JSONDecodeError"

**Solution**: The LLM returned invalid JSON. This can happen with:

- Temperature > 0 (set to 0 for deterministic output)
- Model doesn't support JSON mode
- API issues

Check your `.env` settings.

## Next Steps

1. **Explore the output files** in `data/plans/` and `data/raw/`
2. **Try different queries** to see how the system adapts
3. **Add your own trusted sources** in `config/sources.json`
4. **Check the logs** to understand the flow

## Getting Help

- Read the full [README.md](README.md) for architecture details
- Check file contents in `data/` folders to understand outputs
- Review logs for detailed execution information

## Capabilities

- ✅ Planning and orchestration (Gemini / Ollama)
- ✅ Task routing
- ✅ Data collection
- ✅ Trust validation and credibility scoring
- ✅ SQLite storage with caching
- ✅ Insight generation

---

**You're ready to go! Run `python main.py` and enter a query.**
