# DigitalOcean Community

**Source URL:** [https://www.digitalocean.com/community/](https://www.digitalocean.com/community/)
**Scraped Page:** [https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp)
**Title:** Zero-Infrastructure RAG Agent with Knowledge Bases + MCP | DigitalOcean
**Scraped At:** 2026-07-14T10:34:44.908526Z

---

## Report this 
What is the reason for this report?
This undefined is spam
This undefined is offensive
This undefined is off-topic
This undefined is other
Submit
# Zero-Infrastructure RAG Agent with Knowledge Bases + MCP
Published on June 16, 2026
[Knowledge-Bases](https://www.digitalocean.com/community/tags/knowledge-bases)
[Model Context Protocol](https://www.digitalocean.com/community/tags/mcp)
By [Anish Singh Walia](https://www.digitalocean.com/community/users/asinghwalia)
Sr Technical Content Strategist and Team Lead
Table of contents
Popular topics
##  [Introduction](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp#introduction)
A solo LegalTech founder has 10,000+ internal case files. The product needs an AI assistant that returns grounded answers with source references. The founder does not want to operate a vector database, an embedding service, or a reranker on day one.
**DigitalOcean Knowledge Bases** is a managed [RAG pipeline](https://www.digitalocean.com/resources/articles/rag). You point at files in [Spaces](https://www.digitalocean.com/products/spaces), and the platform handles chunking, embedding, and storage in [Managed OpenSearch](https://docs.digitalocean.com/products/databases/opensearch/). Retrieval is exposed as an MCP tool at `https://kbaas.do-ai.run/v1/mcp`, so agent frameworks call one function instead of wiring five services.
This tutorial differs from older RAG walkthroughs that assemble LangChain + Chroma yourself. Here you use DigitalOcean native infrastructure only: Spaces, Knowledge Bases, MCP, [Serverless Inference](https://docs.digitalocean.com/products/inference/how-to/use-serverless-inference/), and a small **FastAPI** service you deploy to [App Platform](https://docs.digitalocean.com/products/app-platform/).
##  [Key takeaways](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp#key-takeaways)
  * Knowledge Bases indexes PDF, Markdown, HTML, and 15+ text formats from Spaces buckets without you running vector infrastructure.
  * The Knowledge Bases MCP endpoint exposes `retrieve_knowledge_base` for hybrid search with 1 to 25 results per call.
  * MCP retrieval billing matches the [Knowledge Base retrieve API](https://docs.digitalocean.com/products/inference/details/pricing/#knowledge-bases): you pay embedding tokens for query vectorization plus optional reranking tokens.
  * Answer generation is separate. Your FastAPI service bills [Serverless Inference](https://docs.digitalocean.com/products/inference/details/pricing/#serverless-inference) per token (for example, Claude Sonnet 4.6 at $3.00 per 1M input tokens and $15.00 per 1M output tokens for prompts up to 200K tokens).
  * Agent creation on the [Agent Platform](https://docs.digitalocean.com/products/inference/how-to/create-agents/) is free. You pay for model usage, indexing, storage, and retrieval.
  * For production LegalTech workloads, start in **TOR1**. Most Agent Platform infrastructure runs there per [Knowledge Base docs](https://docs.digitalocean.com/products/inference/how-to/create-manage-agent-knowledge-bases/).


##  [When to use Knowledge Bases + MCP and when not to](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp#when-to-use-knowledge-bases-mcp-and-when-not-to)  
| Knowledge Bases + MCP is a good fit  | Try something else  |  
| --- | --- |  
| Static or semi-static document corpora (case files, manuals, policies)  | Live transactional data (CRM rows, ticket state)  |  
| You want hybrid semantic + keyword retrieval with optional reranking  | You only need a single API call with no document grounding  |  
| You want MCP-standard tool access for Cursor, LangChain, or custom agents  | You need sub-10ms retrieval at massive QPS on custom hardware  |  
| You want managed OpenSearch and Spaces storage  | You must run a self-hosted vector DB for policy reasons  |  
| Prototype to production on one cloud  | You already operate a mature RAG stack you prefer to keep  |  
For the RAG vs MCP decision tree at the pattern level, see [Guide to RAG and MCP](https://www.digitalocean.com/community/tutorials/engineers-guide-rag-vs-mcp-llms). This tutorial uses RAG for document grounding and MCP as the tool transport.
##  [Prerequisites](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp#prerequisites)
Before you start, confirm you have:
  * A [DigitalOcean account](https://www.digitalocean.com/pricing).
  * **Inference** and **Agent Platform** access in the [Control Panel](https://cloud.digitalocean.com).
  * A [personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/) with `GenAI:read` for retrieval and MCP, plus `genai` CRUD scopes to create the Knowledge Base via API.
  * A **Model Access Key** from **INFERENCE** → **Serverless Inference** → **Model Access Keys** , or a personal access token with Serverless Inference access (some accounts can use the same PAT as `MODEL_ACCESS_KEY` when dedicated model keys are unavailable).
  * **Knowledge Base Enhancements** preview enabled for advanced chunking and the retrieve endpoint (recommended).
  * Python 3.10+ and [doctl](https://docs.digitalocean.com/reference/doctl/) for local testing and App Platform deploy.


**Lab tip:** Use a sandbox project. Do not upload real client PII for this walkthrough. The sample files in this repo are fictional.
**Note:** You can also use the [DigitalOcean Launch Pad](https://docs.digitalocean.com/products/launchpad/) in the Control Panel to deploy this RAG Agent under the [RAG Assistant Starter Kit](https://docs.digitalocean.com/products/launchpad/#rag-assistant). It follows the same steps that we follow in this tutorial. But for ease of understanding and learning, we will be deploying everything manually.
###  [A quick map of terms](https://www.digitalocean.com/community/tutorials/build-rag-agent-d

... (truncated)
