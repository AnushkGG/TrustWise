# Simon Willison Blog

**Source URL:** [https://simonwillison.net/](https://simonwillison.net/)
**Scraped Page:** [https://simonwillison.net/](https://simonwillison.net/)
**Title:** Simon Willison Blog
**Scraped At:** 2026-04-14T19:29:11.545181Z

---

# Simon Willison’s Weblog
On [coding-agents 190](https://simonwillison.net/tags/coding-agents/) [python 1243](https://simonwillison.net/tags/python/) [google 402](https://simonwillison.net/tags/google/) [pelican-riding-a-bicycle 104](https://simonwillison.net/tags/pelican-riding-a-bicycle/) [llms 1705](https://simonwillison.net/tags/llms/) [...](https://simonwillison.net/tags/)
**Sponsored by:** Teleport — Connect agents to your infra in seconds with Teleport Beams. Built-in identity. Zero secrets. [Get early access](https://fandf.co/4tq0sbV)
## [Entries](https://simonwillison.net/entries/) [Links](https://simonwillison.net/blogmarks/) [Quotes](https://simonwillison.net/quotations/) [Notes](https://simonwillison.net/notes/) [Guides](https://simonwillison.net/guides/) [Elsewhere](https://simonwillison.net/elsewhere/)
### April 13, 2026
[Steve Yegge](https://twitter.com/steve_yegge/status/2043747998740689171):
> I was chatting with my buddy at Google, who's been a tech director there for about 20 years, about their AI adoption. Craziest convo I've had all year.
> The TL;DR is that Google engineering appears to have the same AI adoption footprint as John Deere, the tractor company. Most of the industry has the same internal adoption curve: 20% agentic power users, 20% outright refusers, 60% still using Cursor or equivalent chat tool. It turns out Google has this curve too. [...]
> There has been an industry-wide hiring freeze for 18+ months, during which time nobody has been moving jobs. So there are no clued-in people coming in from the outside to tell Google how far behind they are, how utterly mediocre they have become as an eng org.
[Addy Osmani](https://twitter.com/addyosmani/status/2043812343508021460):
> On behalf of @Google, this post doesn't match the state of agentic coding at our company. Over 40K SWEs use agentic coding weekly here. Googlers have access to our own versions of @antigravity, @geminicli, custom models, skills, CLIs and MCPs for our daily work. Orchestrators, agent loops, virtual SWE teams and many other systems are actively available to folks. [...]
[Demis Hassabis](https://twitter.com/demishassabis/status/2043867486320222333):
> Maybe tell your buddy to do some actual work and to stop spreading absolute nonsense. This post is completely false and just pure clickbait.
[#](https://simonwillison.net/2026/Apr/13/steve-yegge/) [8:59 pm](https://simonwillison.net/2026/Apr/13/steve-yegge/) / [addy-osmani](https://simonwillison.net/tags/addy-osmani/), [steve-yegge](https://simonwillison.net/tags/steve-yegge/), [google](https://simonwillison.net/tags/google/), [generative-ai](https://simonwillison.net/tags/generative-ai/), [agentic-engineering](https://simonwillison.net/tags/agentic-engineering/), [ai](https://simonwillison.net/tags/ai/), [llms](https://simonwillison.net/tags/llms/)
Research [Exploring the new `servo` crate](https://github.com/simonw/research/tree/main/servo-crate-exploration#readme) — After the April 2026 release of the `servo` v0.1.0 crate (blog post), a concise investigation shows that Servo is now an embeddable browser engine for Rust, with a clear API centered on the `ServoBuilder`, `WebView`, and pixel readback methods. A headless CLI (`servo-shot`) successfully renders URLs or HTML files to PNG, building against stable Rust with a robust software-based rendering pipeline.
In [Servo is now available on crates.io](https://servo.org/blog/2026/04/13/servo-0.1.0-release/) the Servo team announced the initial release of the [servo](https://crates.io/crates/servo) crate, which packages their browser engine as an embeddable library.
I set Claude Code for web [the task](https://github.com/simonw/research/pull/108) of figuring out what it can do, building a CLI tool for taking screenshots using it and working out if it could be compiled to WebAssembly.
The `servo-shot` Rust tool it built works pretty well:

```
git clone https://github.com/simonw/research
cd research/servo-crate-exploration/servo-shot
cargo build
./target/debug/servo-shot https://news.ycombinator.com/

```

Here's the result:
Compiling Servo itself to WebAssembly is not feasible due to its heavy use of threads and dependencies like SpiderMonkey, but Claude did build me [this playground page](https://simonw.github.io/research/servo-crate-exploration/html5ever-wasm-demo/www/) for trying out a WebAssembly build of the `html5ever` and `markup5ever_rcdom` crates, providing a tool for turning fragments of HTML into a parse tree.
[13th Apr 2026, 3:04 pm](https://simonwillison.net/2026/Apr/13/servo-crate-exploration/) · [research](https://simonwillison.net/tags/research/), [browsers](https://simonwillison.net/tags/browsers/), [rust](https://simonwillison.net/tags/rust/), [webassembly](https://simonwillison.net/tags/webassembly/), [claude-code](https://simonwillison.net/tags/claude-code/), [servo](https://simonwillison.net/tags/servo/)
> The problem is that LLMs inherently **lack the virtue of laziness**. Work costs nothing to an LLM. LLMs do not feel a need to optimize for their own (or anyone's) future time, and will happily dump more and more onto a layercake of garbage. Left unchecked, LLMs will make systems larger, not better — appealing to perverse vanity metrics, perhaps, but at the cost of everything that matters.
> As such, LLMs highlight how essential our human laziness is: our finite time **forces** us to develop crisp abstractions in part because we don't want to waste our (human!) time on the consequences of clunky ones.
— [Bryan Cantrill](https://bcantrill.dtrace.org/2026/04/12/the-peril-of-laziness-lost/), The peril of laziness lost
[#](https://simonwillison.net/2026/Apr/13/bryan-cantrill/) [2:44 am](https://simonwillison.net/2026/Apr/13/bryan-cantrill/) / [bryan-cantrill](https://simonwillison.net/tags/bryan-cantrill/), [ai](https://simonwillison.net/tags/ai/), [llms](https://simonwillison.net/tags/llms/), [ai-assisted-programming](https://simonwillison.net/tags/ai-assisted-programming

... (truncated)
