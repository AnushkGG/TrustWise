# Schneier on Security

**Source URL:** [https://www.schneier.com/](https://www.schneier.com/)
**Scraped Page:** [https://www.schneier.com/](https://www.schneier.com/)
**Title:** Schneier on Security
**Scraped At:** 2026-04-23T06:40:22.729973Z

---

Schneier on Security -
Search
Powered by
DuckDuckGo
Blog
Essays
Whole site
Subscribe
ICE Uses Graphite Spyware
ICE has
admitted
that it uses spyware from the Israeli company Graphite.
Tags:
homeland security
,
Israel
,
privacy
,
spyware
,
surveillance
Posted on April 22, 2026 at 7:02 AM
•
9 Comments
Mexican Surveillance Company
Grupo Seguritech
is a Mexican surveillance company that is expanding into the US.
Tags:
Mexico
,
privacy
,
surveillance
Posted on April 21, 2026 at 7:04 AM
•
8 Comments
Is “Satoshi Nakamoto” Really Adam Back?
The
New York Times
has a
long article
where the author lays out an impressive array of circumstantial evidence that the inventor of Bitcoin is the cypherpunk Adam Back.
I don’t know. The article is convincing, but it’s written to be convincing.
I can’t remember if I ever met Adam. I was a member of the Cypherpunks mailing list for a while, but I was never really an active participant. I spent more time on the Usenet newsgroup sci.crypt. I knew a bunch of the Cypherpunks, though, from various conferences around the world at the time. I really have no opinion about who Satoshi Nakamoto really is.
Tags:
bitcoin
,
cryptocurrency
,
pseudonymity
Posted on April 20, 2026 at 7:07 AM
•
20 Comments
Friday Squid Blogging: New Giant Squid Video
Pretty fantastic
video
from Japan of a giant squid eating another squid.
As usual, you can also use this squid post to talk about the security stories in the news that I haven’t covered.
Blog moderation policy.
Tags:
squid
,
video
Posted on April 17, 2026 at 5:05 PM
•
26 Comments
Mythos and Cybersecurity
Last week, Anthropic pulled back the curtain on
Claude Mythos Preview
, an AI model so capable at finding and exploiting software vulnerabilities that the company
decided
it was too dangerous to release to the public. Instead, access has been
restricted
to roughly 50 organizations—Microsoft, Apple, Amazon Web Services, CrowdStrike and other vendors of critical infrastructure—under an initiative called
Project Glasswing
.
The announcement was accompanied by a barrage of hair-raising anecdotes:
thousands
of vulnerabilities uncovered across
every major
operating system and browser, including a 27-year-old bug in OpenBSD, a 16-year-old flaw in FFmpeg. Mythos was able to weaponize a set of vulnerabilities it found in the Firefox browser into 181 usable attacks; Anthropic’s previous flagship model could only achieve two.
This is, in many respects, exactly the kind of responsible disclosure that security researchers have long urged. And yet the public has been given remarkably little with which to evaluate Anthropic’s decision. We have been shown a highlight reel of spectacular successes. However, we can’t tell if we have a blockbuster until they let us see the whole movie.
For example, we don’t know how many times Mythos mistakenly flagged code as vulnerable. Anthropic said security contractors agreed with the AI’s severity rating 198 times, with an 89 per cent severity agreement. That’s impressive, but incomplete. Independent researchers examining similar models have found that AI that detects nearly every real bug also hallucinates plausible-sounding vulnerabilities in patched, correct code.
This matters. A model that autonomously finds and exploits hundreds of vulnerabilities with inhuman precision is a game changer, but a model that generates thousands of false alarms and non-working attacks still needs skilled and knowledgeable humans. Without knowing the rate of false alarms in Mythos’s unfiltered output, we cannot tell whether the examples showcased are representative.
There is a second, subtler problem. Large language models, including Mythos, perform best on inputs that resemble what they were trained on: widely used open-source projects, major browsers, the Linux kernel and popular web frameworks. Concentrating early access among the largest vendors of precisely this software is sensible; it lets them patch first, before adversaries catch up.
But the inverse is also true. Software outside the training distribution—industrial control systems, medical device firmware, bespoke financial infrastructure, regional banking software, older embedded systems—is exactly where out-of-the-box Mythos is likely least able to find or exploit bugs.
However, a sufficiently motivated attacker with domain expertise in one of these fields could nevertheless wield Mythos’s advanced reasoning capabilities as a force multiplier, probing systems that Anthropic’s own engineers lack the specialized knowledge to audit. The danger is not that Mythos fails in those domains; it is that Mythos may succeed for whoever brings the expertise.
Broader, structured access for academic researchers and domain specialists—cardiologists’ partners in medical device security, control-systems engineers, researchers in less prominent languages and ecosystems—would meaningfully reduce this asymmetry. Fifty companies, however well chosen, cannot substitute for the distributed expertise of the entire research community.
None of this is an indictment of Anthropic. By all appearances the company is trying to act responsibly, and its decision to hold the model back is evidence of seriousness.
But Anthropic is a private company and, in some ways, still a start-up. Yet it is making unilateral decisions about which pieces of our critical global infrastructure get defended first, and which must wait their turn.
It has finite staff, finite budget and finite expertise. It will miss things, and when the thing missed is in the software running a hospital or a power grid, the cost will be borne by people who never had a say.
The security problem is
far greater
than one company and one model. There’s no reason to believe that Mythos Preview is unique. (Not to be outdone, OpenAI
announced
that its new GPT-5.4-Cyber is so dangerous that the model also will not be released to the general public.) And it’s unclear how much of an advance these new models represent. The security company Aisle w
... (truncated)
