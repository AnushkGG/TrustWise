# Combined Citation Summary

**Query:** Zero-Knowledge RAG
**Sources Scraped:** 12
**Generated At:** 2026-07-14T10:34:45.007478Z

---

## 1. PayPal Engineering

**URL:** [https://medium.com/@aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6](https://medium.com/@aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6)
**Title:** Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction | by Akash Goyal | Medium

[Sitemap](https://medium.com/sitemap/sitemap.xml)
[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)
Sign up
Get app
Sign up
Member-only story
# Ontology-Driven GraphRAG: A Framework for Zero-Noise Knowledge Extraction
17 min read Dec 3, 2025
--
18
--
Share
_Building a self-improving knowledge graph that doesn’t just store data, it understands, validates, and evolves it_
Press enter or click to view image in full size
created by author, credits: gemini
When I first built a GraphRAG system, I did what most tutorials teach: feed documents to an LLM, ask it to extract entities, dump the JSON into Neo4j, and call it a day. It worked beautifully in demos. Then I tried it on real medical records.
The LLM extracted “John Doe, 45” from one report and “John Doe, age 45” from another, creating two separate patient nodes. It found “Type 2 Diabetes” in document A and “T2D” in document B, three different disease nodes for the same condition. The dosage “500mg twice daily” got lost entirely because there was no place to store it in a simple `(Patient)-[PRESCRIBED]->(Medication)` edge.
After processing a thousand clinical reports, my “knowledge graph” was a mess of duplicates, inconsistencies, and missing data. When a doctor asked to trace where a diagnosis came from, I had no answer. The system couldn’t tell me which document, which extraction run, o

... (see full source file for more)

---


## 2. PayPal Engineering

**URL:** [https://medium.com/@priyaskulkarni/from-zero-to-rag-the-beginners-guide-to-retrieval-augmented-generation-739bb6d535d3](https://medium.com/@priyaskulkarni/from-zero-to-rag-the-beginners-guide-to-retrieval-augmented-generation-739bb6d535d3)
**Title:** From Zero to RAG: The Beginner’s Guide to Retrieval-Augmented Generation | by Priya Kulkarni | Medium

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
  1. **They don’t know your private data** They can’t see your internal company docs, Confluence pages, PDFs, or emails unless you give them that information at r

... (see full source file for more)

---


## 3. DigitalOcean Community

**URL:** [https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp)
**Title:** Zero-Infrastructure RAG Agent with Knowledge Bases + MCP | DigitalOcean

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
This tutorial differs from older RAG walkthroughs that assemble LangChain +

... (see full source file for more)

---


## 4. BAIR Blog

**URL:** [https://bair.berkeley.edu/blog/2024/05/29/tiny-agent/](https://bair.berkeley.edu/blog/2024/05/29/tiny-agent/)
**Title:** TinyAgent: Function Calling at the Edge – The Berkeley Artificial Intelligence Research Blog

# TinyAgent: Function Calling at the Edge
[Lutfi Eren Erdogan^*](https://www.linkedin.com/in/lutfi-eren-erdogan-02900b189/), [Nicholas Lee^*](https://www.linkedin.com/in/nicholas-lee-74731916a/), [Siddharth Jha^*](https://sidjha1.github.io), [Sehoon Kim](https://sehoonkim.org), [Ryan Tabrizi](https://ryantabrizi.com), [Suhong Moon](https://www.linkedin.com/in/suhong-moon-5288ab150/), [Coleman Hooper](https://www.linkedin.com/in/coleman-hooper-165061193), [Gopala Anumanchipalli](https://www2.eecs.berkeley.edu/Faculty/Homepages/gopala.html), [Kurt Keutzer](https://people.eecs.berkeley.edu/~keutzer/), [Amir Gholami](http://amirgholami.org/) May 29, 2024 
The ability of LLMs to execute commands through plain language (e.g. English) has enabled agentic systems that can complete a user query by orchestrating the right set of tools (e.g. [ToolFormer](https://arxiv.org/pdf/2302.04761), [Gorilla](https://arxiv.org/pdf/2305.15334)). This, along with the recent multi-modal efforts such as the GPT-4o or Gemini-1.5 model, has expanded the realm of possibilities with AI agents. While this is quite exciting, the large model size and computational requirements of these models often requires their inference to be performed on the cloud. This can create several challenges for their widespread adoption. First and foremost, uploading data such as video, audio, or text documents to a third party vendor on the cloud, can result in privacy issues. Second, this requires cloud/Wi-Fi connectivity whic

... (see full source file for more)

---


## 5. MIT News AI

**URL:** [https://news.mit.edu/2025/teen-builds-vr-prototype-thanks-to-mit-opencourseware-1217](https://news.mit.edu/2025/teen-builds-vr-prototype-thanks-to-mit-opencourseware-1217)
**Title:** Teen builds an award-winning virtual reality prototype thanks to free MIT courses | MIT News | Massachusetts Institute of Technology

[Skip to content ↓](https://news.mit.edu/2025/teen-builds-vr-prototype-thanks-to-mit-opencourseware-1217#main)
[ Massachusetts Institute of Technology](http://web.mit.edu)
See More Results
[Suggestions or feedback?](http://web.mit.edu/feedback)
## Browse By
### Topics
Explore:
  * [Machine learning](https://news.mit.edu/topic/machine-learning)
  * [Sustainability](https://news.mit.edu/topic/sustainability)
  * [Startups](https://news.mit.edu/topic/startups)
  * [Black holes](https://news.mit.edu/topic/black-holes)
  * [Classes and programs](https://news.mit.edu/topic/classes-and-programs)


### Departments
Explore:
  * [Aeronautics and Astronautics](https://news.mit.edu/department/aeronautics-and-astronautics)
  * [Brain and Cognitive Sciences](https://news.mit.edu/department/brain-and-cognitive-sciences)
  * [Architecture](https://news.mit.edu/department/architecture)
  * [Political Science](https://news.mit.edu/department/political-science)
  * [Mechanical Engineering](https://news.mit.edu/department/mechanical-engineering)


### Centers, Labs, & Programs
Explore:
  * [Abdul Latif Jameel Poverty Action Lab (J-PAL)](https://news.mit.edu/clp/abdul-latif-jameel-poverty-action-lab-j-pal)
  * [Picower Institute for Learning and Memory](https://news.mit.edu/clp/picower-institute)
  * [Media Lab](https://news.mit.edu/clp/media-lab)
  * [Lincoln Laboratory](https://news.mit.edu/clp/lincoln-laboratory)


### Schools
  * [School of Architecture + Planning](https://news.mit.edu/school

... (see full source file for more)

---


## 6. MIT News AI

**URL:** [https://news.mit.edu/2019/computing-the-future-mit-turing-award-panel-0305](https://news.mit.edu/2019/computing-the-future-mit-turing-award-panel-0305)
**Title:** Computing the future | MIT News | Massachusetts Institute of Technology

[Skip to content ↓](https://news.mit.edu/2019/computing-the-future-mit-turing-award-panel-0305#main)
[ Massachusetts Institute of Technology](http://web.mit.edu)
See More Results
[Suggestions or feedback?](http://web.mit.edu/feedback)
## Browse By
### Topics
Explore:
  * [Machine learning](https://news.mit.edu/topic/machine-learning)
  * [Sustainability](https://news.mit.edu/topic/sustainability)
  * [Startups](https://news.mit.edu/topic/startups)
  * [Black holes](https://news.mit.edu/topic/black-holes)
  * [Classes and programs](https://news.mit.edu/topic/classes-and-programs)


### Departments
Explore:
  * [Aeronautics and Astronautics](https://news.mit.edu/department/aeronautics-and-astronautics)
  * [Brain and Cognitive Sciences](https://news.mit.edu/department/brain-and-cognitive-sciences)
  * [Architecture](https://news.mit.edu/department/architecture)
  * [Political Science](https://news.mit.edu/department/political-science)
  * [Mechanical Engineering](https://news.mit.edu/department/mechanical-engineering)


### Centers, Labs, & Programs
Explore:
  * [Abdul Latif Jameel Poverty Action Lab (J-PAL)](https://news.mit.edu/clp/abdul-latif-jameel-poverty-action-lab-j-pal)
  * [Picower Institute for Learning and Memory](https://news.mit.edu/clp/picower-institute)
  * [Media Lab](https://news.mit.edu/clp/media-lab)
  * [Lincoln Laboratory](https://news.mit.edu/clp/lincoln-laboratory)


### Schools
  * [School of Architecture + Planning](https://news.mit.edu/school/architect

... (see full source file for more)

---


## 7. Stanford AI Lab Blog

**URL:** [https://ai.stanford.edu/~kaidicao/](https://ai.stanford.edu/~kaidicao/)
**Title:** This is an academic website for Kaidi Cao

Kaidi Cao 
Research @ Anthropic 
I’m a Member of Technical Staff at Anthropic, advancing Claude’s agentic and tool-use capabilities. Before that, I co-founded Voyage AI, built best-in-class embedding and reranking models for AI search, and led it to acquisition. I hold a B.E. from Tsinghua University and a Ph.D. in Computer Science from Stanford. 
Learning Large Graph Property Prediction via Graph Segment Training 
**Kaidi Cao**, Phitchaya Mangpo Phothilimthana, Sami Abu-El-Haija, Dustin Zelle, Yanqi Zhou, Charith Mendis, Jure Leskovec, Bryan Perozzi
NeurIPS, 2023
[[ **Paper**](https://arxiv.org/pdf/2305.12322.pdf)] [[**Code**](https://github.com/kaidic/GST)] 
TpuGraphs: A Performance Prediction Dataset on Large Tensor Computational Graphs 
Phitchaya Mangpo Phothilimthana, Sami Abu-El-Haija, **Kaidi Cao**, Bahare Fatemi, Charith Mendis, Bryan Perozzi
NeurIPS, 2023
[[ **Paper**](https://arxiv.org/pdf/2308.13490.pdf)] [[**Code**](https://github.com/google-research-datasets/tpu_graphs)] 
AutoTransfer: AutoML with Knowledge Transfer - An Application to Graph Neural Networks 
**Kaidi Cao**, Jiaxuan You, Jiaju Liu, Jure Leskovec
ICLR, 2023
[[ **Paper**](https://openreview.net/forum?id=y81ppNf_vg)] [[**Code**](https://github.com/snap-stanford/AutoTransfer)] 
Annotation of Spatially Resolved Single-cell Data with STELLAR 
Maria Brbić*, **Kaidi Cao***, John W. Hickey*, Yuqi Tan, Michael P. Snyder, Garry P. Nolan, Jure Leskovec
Nature Methods, 2022
[[ **Paper**](https://www.nature.com/

... (see full source file for more)

---


## 8. Distill

**URL:** [https://distill.pub/about/](https://distill.pub/about/)
**Title:** Distill is dedicated to making machine learning clear and dynamic

[About](https://distill.pub/about/) [Prize](https://distill.pub/prize/) [Submit](https://distill.pub/journal/)
#  Machine Learning Research Should Be Clear, Dynamic and Vivid. **Distill** Is Here to Help.
### [A Journal Devoted to clear explanations, native to the Web. ](https://distill.pub/journal/) ### [$10,000 Prizes For outstanding work communicating and refining ideas. ](https://distill.pub/prize/)
## Distill was a scientific journal which operated 2016-2021.
We are now on an [indefinite hiatus](https://distill.pub/2021/distill-hiatus/).
## A modern medium for presenting research
The web is a powerful medium to share new ways of thinking. Over the last few years we’ve [seen](http://explorableexplanations.com/) [many](http://cs.stanford.edu/people/karpathy/convnetjs/) [imaginative](http://www.r2d3.us/visual-intro-to-machine-learning-part-1/) [examples](http://colah.github.io/) [of](https://acko.net/tv/toolsforthought/) [such](http://cognitivemedium.com/tat/) [work](http://worrydream.com/MediaForThinkingTheUnthinkable/). But traditional academic publishing remains focused on the PDF, which prevents this sort of communication.
[Reactive diagrams](http://distill.pub/2016/augmented-rnns/) allow for a type of communication not possible in static mediums. Hover over this diagram to see how a neural turing machine shifts its attention over its old memory values to create new values.
## New ways of thinking enable new discoveries
New notations, visualizations, and mental models c

... (see full source file for more)

---


## 9. NeurIPS Blog

**URL:** [https://blog.neurips.cc/category/2026-conference/](https://blog.neurips.cc/category/2026-conference/)
**Title:** 2026 Conference – NeurIPS Blog

[Skip to content](https://blog.neurips.cc/category/2026-conference/#content)
# 2026 Conference 
July 3 2026
## [NeurIPS Newsletter – June 2026](https://blog.neurips.cc/2026/07/03/neurips-newsletter-june-2026/)
[Communication Chairs 2026](https://blog.neurips.cc/author/jeankossaifi/) [2026 Conference](https://blog.neurips.cc/category/2026-conference/), [NeurIPS Newsletters](https://blog.neurips.cc/category/general/neurips-newsletters/) [neurips2026](https://blog.neurips.cc/tag/neurips2026/), [newsletter](https://blog.neurips.cc/tag/newsletter/)
Welcome to the June edition of the NeurIPS monthly Newsletter!
The NeurIPS Newsletter aims to provide an easy way to keep up to date with NeurIPS events and planning progress, respond to requests for feedback and participation, and find information about new initiatives. This newsletter will focus on **NeurIPS 2026** , held in **Sydney** , **Australia** , with official Satellites in Atlanta, USA and Paris, France. The conference will be held on the following dates:
  * Sydney, Australia: from **Sunday,** **Dec 6th to Saturday, Dec 12th**
  * Atlanta, USA: from **Tuesday Dec 8th to Sunday Dec 13th**
  * Paris, France: from **Wednesday Dec 9th to Sunday Dec 13th**


You are receiving this newsletter as per your subscription preferences in your NeurIPS profile. As you prepare to attend NeurIPS, we hope that you will find the following information valuable.
This NeurIPS Newsletter includes:
  1. Updates in the Position Paper Track
  2. Remi

... (see full source file for more)

---


## 10. NeurIPS Blog

**URL:** [https://blog.neurips.cc/2025/06/27/neurips-2025-competitions-announced/](https://blog.neurips.cc/2025/06/27/neurips-2025-competitions-announced/)
**Title:** NeurIPS 2025 Competitions Announced – NeurIPS Blog

[Skip to content](https://blog.neurips.cc/2025/06/27/neurips-2025-competitions-announced/#content)
June 27 2025
# [NeurIPS 2025 Competitions Announced](https://blog.neurips.cc/2025/06/27/neurips-2025-competitions-announced/)
[Communications Chairs 2025](https://blog.neurips.cc/author/mengyeren/)
Today, we introduce the competitions that have been accepted at NeurIPS 2025 Competition Track. It seemed especially challenging this year given the number of quality submissions and the limited number that could be accepted compared to last year. We finally selected a total of 18 very strong proposals, covering a wide range of areas and sub-disciplines. Some of the competitions are completely new, and others are familiar to the NeurIPS community. 
This year will mark the ninth year of NeurIPS having a dedicated competition track. Whether this is the first time you’ve heard about NeurIPS competitions or you’re a grandmaster, this year’s cohort has something to offer for a variety of backgrounds, skill levels, and domain knowledge. We hope you’ll take some time to look over this year’s exciting set of competitions, and encourage you to participate! 
Competitions have a valuable place in research and in solving complex problems.
As a participant, you will benefit from being exposed to a vibrant community! Indeed, they’re great for connecting to like-minded researchers, excellent for learning and resume building, and allow you to use your skills to have a real-world impact on important a

... (see full source file for more)

---


## 11. Google AI Blog

**URL:** [https://ai.googleblog.com/2010/12/6-million-to-faculty-in-q4-research.html#!/2010/12/6-million-to-faculty-in-q4-research.html](https://ai.googleblog.com/2010/12/6-million-to-faculty-in-q4-research.html#!/2010/12/6-million-to-faculty-in-q4-research.html)
**Title:** $6 million to faculty in Q4 Research Awards – Google Research Blog

[Skip to main content](https://research.google/blog/6-million-to-faculty-in-q4-research-awards/#page-content)
# $6 million to faculty in Q4 Research Awards
December 8, 2010
Maggie Johnson, Director of Education and University Relations
## Quick links
  * Share
    * Copy link


We've just completed the latest round of Google Research Awards, our program which identifies and supports faculty pursuing research in areas of mutual interest. We had a record number of submissions this round, and are funding 112 awards across 20 different areas—for a total of more than $6 million. We’re also providing more than 150 Android devices for research and curriculum development to faculty whose projects rely heavily on Android hardware.The areas that received the highest level of funding, due to the large number of proposals in these areas, were systems and infrastructure, human computer interaction, security and multimedia. We also continue to support international research; in this round, 29 percent of the funding was awarded to universities outside the U.S.Some examples from this round of awards:
  * **Injong Rhee, North Carolina State University**. Experimental Evaluation of Increasing TCP Initial Congestion Window (Systems)
  * **James Jones, University of California, Irvine**. Bug Comprehension Techniques to Assist Software Debugging (Software Engineering)
  * **Yonina Eldar, Technion, Israel**. Semi-Supervised Regression with Auxiliary Knowledge (Machine Learning)
  * **Victor Lavren

... (see full source file for more)

---


## 12. DeepMind Blog

**URL:** [https://deepmind.google/models/gemini/flash-lite/](https://deepmind.google/models/gemini/flash-lite/)
**Title:** Gemini 3.1 Flash-Lite — Google DeepMind

[Skip to main content](https://deepmind.google/models/gemini/flash-lite/#page-content)
# Gemini 3.1 Flash-Lite
Best for high-volume tasks that need efficiency and intelligence
[ Build with Gemini ](https://aistudio.google.com/prompts/new_chat?model=gemini-3.1-flash-lite-preview&utm_source=deepmind.google&utm_medium=referral&utm_campaign=gdm&utm_content=)
Your browser does not support the video tag.
Introducing 3.1 Flash-Lite, a scalable thinking model for high-volume tasks at low cost and latency.
  * [ Capabilities ](https://deepmind.google/models/gemini/flash-lite/#capabilities)
  * [ Model information ](https://deepmind.google/models/gemini/flash-lite/#model-information)


## Try Gemini 3.1 Flash-Lite
Handles tasks of varying complexity like coding, UI generation and translation with high quality
Slide 1 of 3
### Flexible reasoning levels
Delivers improved reasoning and output quality, allowing users to select the level of thinking they want to use.
### Low latency
Tackles high-volume tasks with faster response times.
### Tool use
Delivers high throughput with quality using search grounding and enhanced instruction following.
### Cost-efficient
Our most cost efficient model yet in the 3 series.
## Hands-on
Explore what you can do with Gemini 3.1 Flash-Lite
Slide 1 of 2
Your browser does not support the video tag.
### Develop real-time e-commerce categories
Gemini 3.1 Flash-Lite populates an e-commerce wireframe with hundreds of products across multiple categories in second

... (see full source file for more)

---


## Source Links

1. [PayPal Engineering](https://medium.com/@aiwithakashgoyal/beyond-simple-extraction-how-production-grade-ontologies-transform-graphrag-from-prototype-to-333742fa41a6)
2. [PayPal Engineering](https://medium.com/@priyaskulkarni/from-zero-to-rag-the-beginners-guide-to-retrieval-augmented-generation-739bb6d535d3)
3. [DigitalOcean Community](https://www.digitalocean.com/community/tutorials/build-rag-agent-digitalocean-knowledge-bases-mcp)
4. [BAIR Blog](https://bair.berkeley.edu/blog/2024/05/29/tiny-agent/)
5. [MIT News AI](https://news.mit.edu/2025/teen-builds-vr-prototype-thanks-to-mit-opencourseware-1217)
6. [MIT News AI](https://news.mit.edu/2019/computing-the-future-mit-turing-award-panel-0305)
7. [Stanford AI Lab Blog](https://ai.stanford.edu/~kaidicao/)
8. [Distill](https://distill.pub/about/)
9. [NeurIPS Blog](https://blog.neurips.cc/category/2026-conference/)
10. [NeurIPS Blog](https://blog.neurips.cc/2025/06/27/neurips-2025-competitions-announced/)
11. [Google AI Blog](https://ai.googleblog.com/2010/12/6-million-to-faculty-in-q4-research.html#!/2010/12/6-million-to-faculty-in-q4-research.html)
12. [DeepMind Blog](https://deepmind.google/models/gemini/flash-lite/)
