# DeepMind Blog

**Source URL:** [https://deepmind.google/](https://deepmind.google/)
**Scraped Page:** [https://deepmind.google/models/gemini/flash-lite/](https://deepmind.google/models/gemini/flash-lite/)
**Title:** Gemini 3.1 Flash-Lite — Google DeepMind
**Scraped At:** 2026-07-14T10:34:45.002327Z

---

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
Gemini 3.1 Flash-Lite populates an e-commerce wireframe with hundreds of products across multiple categories in seconds.
Your browser does not support the video tag.
### Build a generative weather dashboard
Gemini 3.1 Flash-Lite builds live weather dashboards on demand, pulling real-time forecasts and historical data into dynamic visualizations.
## Showcase
Slide 1 of 4
> Google’s model has demonstrated unparalleled instruction-following capabilities and speed in its class, achieving 20% higher success rate and 60% faster inference times than our previous model. It's enabling Latitude to deliver sophisticated storytelling to a much wider audience than would have otherwise been possible.
Kolby Nottingham
Head of AI, Latitude
> 3.1 Flash-Lite is a remarkably competent model. It is lightning fast, but still somehow finds a way to follow all instructions. It is great at tool calling and can rapidly explore codebases in a fraction of the time of bigger models. We have a wide variety of multimodal labeling use cases, at dramatic scale, we’ve found Flash-Lite to be an unlock for our ability to bring insight to more data at even larger scale. The intelligence to speed ratio is unparalleled in any other model.
Andrew Carr
Chief Scientist, Cartwheel
> By integrating 3.1 Flash-Lite into our classification pipeline, Whering has achieved 100% consistency in item tagging, providing a highly reliable foundation for our label assignment. 3.1 Flash-Lite’s ability to deliver certain, repeatable results, even on complex fashion categories, has streamlined our data labelling process and increased our confidence in the structured outputs.
Bianca Rangecroft
CEO, Whering
> As a root orchestration and content engine 3.1 Flash-Lite consistently delivered sub-10 second completions with near-instant streaming, ~97% structured output compliance, and 94% intent routing accuracy. For high-throughput AI products, it offers an exceptional balance of speed, instruction fidelity, and cost efficiency.
Kaan Ortabas
Co-Founder, HubX
## Performance
3.1 Flash-Lite performs significantly better than 2.5 Flash across a number of key benchmarks, including general quality, reasoning, translation and factuality.  
| Benchmark  | Notes  | Gemini 3.1Flash-Lite High  | Gemini 2.5Flash Dynamic  | Gemini 2.5Flash-Lite Dynamic  | GPT-5mini High  | Claude 4.5Haiku Extended Thinking  | Grok 4.1Fast Reasoning  |  
| --- | --- | --- | --- | --- | --- | --- | --- |  
| Input price $/1M tokens, no caching  | Lower is better  | $0.25  | $0.30  | $0.10  | $0.25  | $1.00  | $0.20  |  
| Output price $/1M tokens  | Lower is better  | $1.50  | $2.50  | $0.40  | $2.00  | $5.00  | $0.50  |  
| Output speed Tokens / s  | 363  | 249  | 366  | 71  | 108  | 145  |  
| Humanity’s Last Exam Academic reasoning (full set, text + MM)  | No tools  | 16.0%  | 11.0%  | 6.9%  | 16.7%  | 9.7%  | **17.6%**  |  
| GPQA Diamond Scientific knowledge  | No tools  | **86.9%**  | 82.8%  | 66.7%  | 82.3%  | 73.0%  | 84.3%  |  
| MMMU-Pro Multimodal understanding and reasoning  | No tools  | **76.8%**  | 66.7%  | 51.0%  | 74.1%  | 58.0%  | 63.0%  |  
| CharXiv Reasoning Information synthesis from complex charts  | 73.2%  | 63.7%  | 55.5%  |  **75.5%** (+ python)  | 61.7%  | 31.6%  |  
| Video-MMMU Knowledge acquisition from videos  | **84.8%**  | 79.2%  | 60.7%  | 82.5%  | —  | 74.6%  |  
| SimpleQA Verified Parametric knowledge  | **43.3%**  | 28.1%  | 11.5%  | 9.5%  | 5.5%  | 19.5%  |  
| FACTS Benchmark Suite Factuality benchmark across grounding, parametric, search, and MM.  | 40.6%  | **50.4%**  | 17.9%  | 33.7%  | 18.6%  | 42.1%  |  
| MMMLU Multilingual Q&A  | **88.9%**  | 86.6%  | 84.5%  | 84.9%  | 83.0%  | 86.8%  |  
| LiveCodeBench Code generation (UI: 1/1/2025-5/1/2025)  | 72.0%  | 62.6%  | 34.3%  | **80.4%**  | 53.2%  | 76.5%  |  
| MRCR v2 (8-needle) Long context performance  | 128k (average)  | **60.1%**  | 54.3%  | 30.6%  | 52.5%  | 35.3%  | 54.6%  |  
| 1M (pointwise)  | 12.3%  | **21.0%**  | 5.4%  | Not supported  | Not supported  | 6.1%  |  
Methodology: [deepmind.google/models/evals-methodology/gemini-3-1-flash-lite](https://deepmind.google/models/evals-methodology/gemini-3-1-flash-lite)
## Model information 

Name
    3.1 Flash-Lite 

Status
    Preview 

Input
    
  * Text
  * Image
  * Video
  * Audio
  * PDF

text_snippet image videocam mic drive_pdf 

Output
    
  * Text

text_snippet image videocam mic drive_pdf 

Input tokens
    1M 

Output tokens
    64k 

Knowledge cutoff
    January 2025 

Tool use
    
  * Function calling
  * Structured output
  * Search as a tool
  * Code execution


... (truncated)
