# TrustWise architecture

This document complements [README.md](../README.md) and [IMPLEMENTATION.md](../IMPLEMENTATION.md) with diagrams. The LLM produces **structured plan JSON only**; collection, trust, and storage run in separate stages ([implementationtest.md](../implementationtest.md)).

## End-to-end pipeline

The runtime path from a natural-language query to stored insights:

```mermaid
flowchart LR
  subgraph inputLayer [Input]
    userQuery[UserQuery]
  end
  subgraph planLayer [Planning]
    orchestrator[Orchestrator]
    chunker[Chunker]
    scheduler[Scheduler]
  end
  subgraph collectLayer [Collection]
    webAgent[WebAgent]
    researchAgent[ResearchAgent]
  end
  subgraph postLayer [PostProcessing]
    cleaner[Cleaner]
    trustModule[Trust]
    storageModule[Storage]
    insightsModule[Insights]
  end
  userQuery --> orchestrator
  orchestrator -->|"plan JSON"| chunker
  chunker --> scheduler
  scheduler --> webAgent
  scheduler --> researchAgent
  webAgent --> cleaner
  researchAgent --> cleaner
  cleaner --> trustModule
  trustModule --> storageModule
  storageModule --> insightsModule
```

The planner (`call_llm` in `orchestrator/llm_client.py`) outputs **only** a validated execution plan, not final answers or trusted records.

## Planner versus execution boundary

```mermaid
flowchart TB
  llmCall[call_llm]
  planJson[ValidatedPlanJSON]
  downstream[ChunkerSchedulerAgentsCleanerTrustStorage]
  llmCall -->|"JSON plan"| planJson
  planJson --> downstream
```

Downstream stages use the plan to fetch and process data. They are **not** replaced by a single LLM completion; trust scoring and persistence remain explicit.

## Repository layout

High-level map of the main Python packages, bridge, web server, and data directories:

```mermaid
flowchart TB
  subgraph pyPipeline [Python pipeline]
    orchestratorPkg[orchestrator]
    chunkerPkg[chunker]
    schedulerPkg[scheduler]
    agentsPkg[agents]
    cleanerPkg[cleaner]
    trustPkg[trust]
    storagePkg[storage]
    insightsPkg[insights]
    utilsPkg[utils]
  end
  subgraph entrypoints [Entry and IO]
    mainPy[main.py]
    apiBridge[api_bridge.py]
    dataDir[data]
  end
  subgraph webStack [TypeScript web]
    webDir[web]
  end
  mainPy --> orchestratorPkg
  apiBridge --> orchestratorPkg
  orchestratorPkg --> chunkerPkg
  chunkerPkg --> schedulerPkg
  schedulerPkg --> agentsPkg
  agentsPkg --> cleanerPkg
  cleanerPkg --> trustPkg
  trustPkg --> storagePkg
  storagePkg --> insightsPkg
  utilsPkg -.-> orchestratorPkg
  agentsPkg --> dataDir
  webDir -->|"subprocess"| apiBridge
```

## Web UI and API bridge

How the browser reaches the same pipeline as the CLI (`main.py`):

```mermaid
flowchart LR
  browser[Browser]
  expressApp[ExpressServer]
  bridgeProc[api_bridge.py]
  pipeline[PythonPipeline]
  browser -->|"HTTP"| expressApp
  expressApp -->|"stdin JSON stdout JSON"| bridgeProc
  bridgeProc --> pipeline
```

Express is implemented in `web/src/server.ts`. It spawns `api_bridge.py` with the repo root as working directory; optional `PYTHON_EXE` / `TRUSTWISE_PYTHON` selects the interpreter.

## LLM provider modes

Configured via `LLM_PROVIDER` in `.env` (see `.env.example`). Resolution is implemented in `orchestrator/llm_client.py`.

```mermaid
flowchart TB
  providerMode{LLM_PROVIDER}
  ollamaPath[Ollama_local]
  geminiPath[Gemini_cloud]
  bothPath[Parallel_merge]
  providerMode -->|ollama| ollamaPath
  providerMode -->|gemini| geminiPath
  providerMode -->|both| bothPath
```

All modes still produce **plan JSON** for the same downstream pipeline.

## Request/Response Lifecycle (Sequence Diagram)

The following sequence diagram illustrates the handoff between the TypeScript frontend and the Python research pipeline:

```mermaid
sequenceDiagram
  participant User
  participant Browser
  participant Express (TS)
  participant Bridge (PY)
  participant LLM (Ollama/Gemini)
  participant Agents
  participant DB (SQLite)

  User->>Browser: Enters query
  Browser->>Express (TS): POST /api/submit
  Express (TS) ->> Bridge (PY): spawn(python api_bridge.py)
  Bridge (PY) ->> LLM (Ollama/Gemini): Generate research plan
  LLM (Ollama/Gemini) -->> Bridge (PY): Plan JSON
  Bridge (PY) ->> Agents: Parallel task execution
  Agents -->> Bridge (PY): Raw JSON results
  Bridge (PY) ->> Bridge (PY): Process (Clean -> Trust -> Insight)
  Bridge (PY) ->> DB (SQLite): Save trusted items
  Bridge (PY) -->> Express (TS): Combined JSON result (stdout)
  Express (TS) -->> Browser: 200 OK (Full Result)
  Browser ->> User: Display strategic insights
```

## Zero-Trust Validation State Machine

How a raw data item matures into a **Trusted Insight**:

```mermaid
stateDiagram-v2
  [*] --> RawData: Agent collection
  RawData --> Normalized: Cleaner (Schema mapping)
  Normalized --> Validated: Trust Validator (Scoring)
  
  state Validated {
    [*] --> Scored
    Scored --> Passed: Score > Threshold
    Scored --> Dropped: Score <= Threshold
  }

  Passed --> Stored: SQLite persistence
  Dropped --> [*]: Audit trail only
  Stored --> Synthesized: Insight generation
  Synthesized --> [*]: Strategic Result
```

## Component Interconnect Map

A detailed view of and dependency relationships between core services:

```mermaid
graph TB
  subgraph frontend [Frontend Experience]
    ui[React/TS Web UI]
    apiClient[API Bridge Client]
  end

  subgraph apiLayer [API Core]
    expressSrv[Express Server]
    bridgeLogic[api_bridge.py Dispatcher]
  end

  subgraph pipelineCore [Pipeline Core]
    planEngine[Orchestration Engine]
    executor[Chunker & Scheduler]
    trustEngine[Zero-Trust Scoring]
    insightEngine[Insight Synthesis]
  end

  subgraph sourceLayer [Research Sources]
    academic[Academic Source Academy (OpenAlex, etc.)]
    web[Web Search Academy (Tavily, etc.)]
  end

  ui --> apiClient
  apiClient --> expressSrv
  expressSrv --> bridgeLogic
  bridgeLogic --> planEngine
  planEngine --> executor
  executor --> academic
  executor --> web
  academic --> trustEngine
  web --> trustEngine
  trustEngine --> insightEngine
```

---

## Technical Specifications
Detailed REST contracts and internal function signatures are documented in:
- [PRD.md](PRD.md) — Product & Functional Requirements
- [BRD.md](BRD.md) — Business Value & Success KPIs
- [FRONTEND.md](../FRONTEND.md) — Full API Endpoint Specifications
