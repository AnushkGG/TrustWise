# PayPal Engineering

**Source URL:** [https://medium.com/paypal-engineering](https://medium.com/paypal-engineering)
**Scraped Page:** [https://medium.com/@priyaskulkarni/from-zero-to-rag-the-beginners-guide-to-retrieval-augmented-generation-739bb6d535d3](https://medium.com/@priyaskulkarni/from-zero-to-rag-the-beginners-guide-to-retrieval-augmented-generation-739bb6d535d3)
**Title:** From Zero to RAG: The Beginner’s Guide to Retrieval-Augmented Generation | by Priya Kulkarni | Medium
**Scraped At:** 2026-07-14T10:34:44.874456Z

---

[Sitemap](https://medium.com/sitemap/sitemap.xml)
[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)
Sign up
Get app
Sign up
# From Zero to RAG: The Beginner’s Guide to Retrieval-Augmented Generation
4 min read Nov 17, 2025
--
--
Share
What RAG is, why it matters, and how its core building blocks fit together.
## Introduction
If you’ve spent any time around AI people lately, you’ve probably heard the phrase **“RAG system”** thrown around like it’s the most normal thing in the world.
> _“We just slapped a RAG layer on top of our docs.” “Let’s build a RAG chatbot for our knowledge base.”_
But what _is_ RAG, really? And more importantly, how does it work under the hood?
In this article, I’ll walk you through RAG step by step:
  * What Retrieval-Augmented Generation actually means
  * Why using _just_ a large language model (LLM) isn’t enough
  * The four core building blocks: **retriever, generator, index, and prompt**
  * A tiny mental model you can keep in your head


By the end, you won’t just know the buzzword — you’ll understand how RAG systems are designed.
## 1. Why RAG Exists in the First Place
Large Language Models (LLMs) like GPT are powerful… but they have limitations:
  1. **They don’t know your private data** They can’t see your internal company docs, Confluence pages, PDFs, or emails unless you give them that information at runtime.
  2. **They go out of date** Models are trained up to a certain point in time. Anything after that — new product launches, updated policies, new research — won’t be inside the model.
  3. **They hallucinate** When they don’t know something, they’ll often _guess_ in a very confident tone. That’s dangerous in domains like medical, legal, and finance.


So we need a way to:
  * Keep the fluency and reasoning power of LLMs,
  * But **ground** them in _our own data_ , in _real documents_ , at _query time_.


That’s exactly what **Retrieval-Augmented Generation** does.
## 2. What Is RAG? The One-Sentence Definition
**RAG = Retrieval-Augmented Generation.**
In simple terms:
> _Before the model answers, it_** _retrieves relevant information_** _from an external knowledge source and uses it as_** _context_** _to generate a grounded answer._
The typical RAG pipeline looks like this:
> **_User Question → Retrieve relevant context → Feed to LLM → LLM generates answer using that context_**
This is very different from just saying:
> _“Hey model, tell me about X.”_
Instead, you’re saying:
> _“Here are some documents about X. Read these and then answer.”_
## 3. The Four Core Components of a RAG System
When people say “RAG system,” under the hood they’re usually talking about four main parts:
  1. **Retriever** — finds relevant chunks of text or data
  2. **Generator (LLM)** — writes the final answer
  3. **Index (Vector Store)** — stores your data and makes retrieval fast
  4. **Prompt** — tells the LLM how to use the retrieved context


Let’s go through them one by one.
### 3.1 Retriever
The **retriever** is the part that answers:
> _“Given this question, which pieces of text should I show to the model?”_
A typical retriever:
  1. Splits documents into **chunks** (say 200–500 tokens).
  2. Computes **embeddings** for each chunk (vectors that represent meaning).
  3. Stores those vectors in a **vector database**.
  4. At query time, it:


  * embeds the user’s question,
  * finds the **k most similar** embeddings,
  * returns the corresponding chunks.


Good retrieval is crucial. If you retrieve garbage, the model will generate with garbage.
### 3.2 Generator (LLM)
The **generator** is the LLM itself (GPT, Claude, Llama, etc.).
## Get Priya Kulkarni’s stories in your inbox
Join Medium for free to get updates from this writer.
Subscribe
Subscribe
Remember me for faster sign in
It takes a specially constructed **prompt** that includes:
  * Instructions (“use only the context,” “cite sources,” etc.),
  * The **retrieved context** (the chunks we just found),
  * The **user’s question**.


Then it generates an answer.
The magic of RAG is that:
  * The LLM doesn’t need to _know_ your documents ahead of time.
  * You simply show the relevant parts at the time of the question.


### 3.3 Index (Vector Store)
The **index** is how you store and search your chunk embeddings efficiently.
For small demos, you can get away with:
  * a list of vectors,
  * cosine similarity.


For anything non-trivial, you’ll typically use a **vector store** like:
  * **FAISS** — a fast similarity search library
  * **Chroma** — an open-source vector database
  * **Pinecone** — a managed cloud vector database


These tools are built to handle **millions** of embeddings, with fast searches and useful features like metadata filtering.
### 3.4 Prompt
The **prompt** is the “glue” between retrieval and generation.
A good RAG prompt:
  * Tells the model _what role_ it’s playing.
  * Provides the retrieved context.
  * Includes the user question.
  * Explicitly instructs the model to:
  * use only the context,
  * avoid guessing,
  * say “I don’t know” if needed,
  * and ideally, **cite sources**.


Example skeleton:

```
You are a helpful assistant that answers questions using the provided context.If the answer is not in the context, say "I don't know".Cite sources in square brackets like [doc1].Context:[doc1] ...[doc2] ...User question:...Answer:
```

## 4. A Simple Mental Model to Remember
When you hear “RAG,” think:
  1. **Search** — “What should the model read?”
  2. **Synthesize** — “Given what it read, what’s the best answer?”


Or more visually:

```
   ┌───────────────┐      ┌─────────────┐      ┌───────────────┐   │ User Question │ ---> │ Retriever   │ ---> │   LLM (Gen)   │   └───────────────┘      └─────────────┘      └───────────────┘                                 │                                 ▼                           Docs / Index
```

## 5. 

... (truncated)
