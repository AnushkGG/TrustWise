# Schneier on Security

**Source URL:** [https://www.schneier.com/](https://www.schneier.com/)
**Scraped Page:** [https://www.schneier.com/](https://www.schneier.com/)
**Title:** Schneier on Security
**Scraped At:** 2026-04-15T08:19:44.290476Z

---

Schneier on Security -
Search
Powered by
DuckDuckGo
Blog
Essays
Whole site
Subscribe
Upcoming Speaking Engagements
This is a current list of where and when I am scheduled to speak:
I’m speaking at
DemocracyXChange 2026
in Toronto, Ontario, Canada, on April 18, 2026.
I’m speaking at the
SANS AI Cybersecurity Summit 2026
in Arlington, Virginia, USA, at 9:40 AM ET on April 20, 2026.
I’m speaking at the
Greater Good Gathering
in New York City, USA, on Tuesday, April 21, 2026.
I’m speaking at the
Nemertes [Next] Virtual Conference Spring 2026
, a virtual event, on April 29, 2026.
I’m speaking at
RightsCon 2026
in Lusaka, Zambia, on May 6 and 7, 2026.
I’m giving a keynote address and participating in a panel discussion at an ICTLuxembourg event called “
Europe at the Crossroads of AI, Power & the Future of Democracy
.” The event will be held at the University of Luxembourg’s Belval Campus on May 12, 2026.
I’m speaking at the
Potsdam Conference on National Cybersecurity
at the Hasso Plattner Institut in Potsdam, Germany. The event runs June 24–25, 2026, and my talk will be the evening of June 24.
I’m speaking at the
Digital Humanism Conference
in Vienna, Austria, on Tuesday, June 26, 2026.
I’m speaking at the
Nuremberg Digital Festival
in Nuremburg, Germany, on Wednesday, July 1, 2026.
The list is maintained on
this page
.
Tags:
Schneier news
Posted on April 14, 2026 at 12:01 PM
•
2 Comments
How Hackers Are Thinking About AI
Interesting paper: “
What hackers talk about when they talk about AI: Early-stage diffusion of a cybercrime innovation.
”
Abstract:
The rapid expansion of artificial intelligence (AI) is raising concerns about its potential to transform cybercrime. Beyond empowering novice offenders, AI stands to intensify the scale and sophistication of attacks by seasoned cybercriminals. This paper examines the evolving relationship between cybercriminals and AI using a unique dataset from a cyber threat intelligence platform. Analyzing more than 160 cybercrime forum conversations collected over seven months, our research reveals how cybercriminals understand AI and discuss how they can exploit its capabilities. Their exchanges reflect growing curiosity about AI’s criminal applications through legal tools and dedicated criminal tools, but also doubts and anxieties about AI’s effectiveness and its effects on their business models and operational security. The study documents attempts to misuse legitimate AI tools and develop bespoke models tailored for illicit purposes. Combining the diffusion of innovation framework with thematic analysis, the paper provides an in-depth view of emerging AI-enabled cybercrime and offers practical insights for law enforcement and policymakers.
Tags:
academic papers
,
AI
,
cybercrime
,
hacking
Posted on April 14, 2026 at 6:49 AM
•
4 Comments
On Anthropic’s Mythos Preview and Project Glasswing
The cybersecurity industry is obsessing over Anthropic’s new model, Claude Mythos Preview, and its effects on cybersecurity. Anthropic said that it is
not releasing it
to the general public because of its cyberattack capabilities, and has launched
Project Glasswing
to run the model against a whole slew of public domain and proprietary software, with the aim of finding and patching all the vulnerabilities before hackers get their hands on the model and exploit them.
There’s a lot here, and I hope to write something more considered in the coming week, but I want to make some quick observations.
One: This is very much a PR play by Anthropic—and it worked. Lots of reporters are
breathlessly
repeating
Anthropic’s
talking
points
, without engaging with them critically. OpenAI, presumably pissed that Anthropic’s new model has gotten so much positive press and wanting to grab some of the spotlight for itself, announced its model is
just as scary
, and won’t be released to the general public, either.
Two: These models do demonstrate an increased sophistication in their cyberattack capabilities. They write effective exploits—taking the vulnerabilities they find and operationalizing them—without human involvement. They can find more complex vulnerabilities: chaining together several memory corruption bugs, for example. And they can do more with one-shot prompting, without requiring orchestration and agent configuration infrastructure.
Three: Anthropic might have a good PR team, but the problem isn’t with Mythos Preview. The security company Aisle was able to
replicate
the vulnerabilities that Anthropic found, using older, cheaper, public models. But there is a difference between finding a vulnerability and turning it into an attack.  This points to a current advantage to the defender. Finding for the purposes of fixing is easier for an AI than finding plus exploiting. This advantage is likely to shrink, as ever more powerful models become available to the general public.
Four: Everyone who is panicking about the ramifications of this is correct about the problem, even if we can’t predict the exact timeline. Maybe the sea change just happened, with the new models from Anthropic and OpenAI. Maybe it happened six months ago. Maybe it’ll happen in six months. It will happen—I have no doubt about it—and sooner than we are ready for. We can’t predict how much more these models will improve in general, but software seems to be a specialized language that is optimal for AIs.
A couple of weeks ago, I
wrote about
security in what I called “the age of instant software,” where AIs are superhumanly good at finding, exploiting, and patching vulnerabilities. I stand by everything I wrote there. The urgency is now greater than ever.
I was also part of a large team that wrote a “
what to do now
” report. The guidance is largely correct: We need to prepare for a world where zero-day exploits are dime-a-dozen, and lots of attackers suddenly have offensive capabilities that far outstrip their skills.
Tags:
AI
,
cyberattack
,
cybersecurity
,
exploits
,
vulnerabilities
Posted on April 13, 2026 at 12:52
... (truncated)
