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

## Related documentation

- [FRONTEND.md](../FRONTEND.md) — REST contract and payloads
- [orchestrator/llm_client.py](../orchestrator/llm_client.py) — provider calls and merge logic
