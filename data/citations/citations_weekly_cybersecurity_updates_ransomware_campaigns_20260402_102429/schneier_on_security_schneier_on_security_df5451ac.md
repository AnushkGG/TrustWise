# Schneier on Security

**Source URL:** [https://www.schneier.com/](https://www.schneier.com/)
**Scraped Page:** [https://www.schneier.com/](https://www.schneier.com/)
**Title:** Schneier on Security
**Scraped At:** 2026-04-02T10:24:31.929181Z

---

Schneier on Security -
Search
Powered by
DuckDuckGo
Blog
Essays
Whole site
Subscribe
Possible US Government iPhone Hacking Tool Leaked
Wired
writes
(alternate
source
):
Security researchers at Google on Tuesday
released a report
describing what they’re calling “Coruna,” a highly sophisticated iPhone hacking toolkit that includes five complete hacking techniques capable of bypassing all the defenses of an iPhone to silently install malware on a device when it visits a website containing the exploitation code. In total, Coruna takes advantage of 23 distinct vulnerabilities in iOS, a rare collection of hacking components that suggests it was created by a well-resourced, likely state-sponsored group of hackers.
[…]
Coruna’s code also appears to have been originally written by English-speaking coders, notes iVerify’s cofounder Rocky Cole. “It’s highly sophisticated, took millions of dollars to develop, and it bears the hallmarks of other modules that have been publicly attributed to the US government,” Cole tells WIRED. “This is the first example we’ve seen of very likely US government tools­based on what the code is telling us­spinning out of control and being used by both our adversaries and cybercriminal groups.”
TechCrunch
reports
that Coruna is definitely of US origin:
Two former employees of government contractor L3Harris told TechCrunch that Coruna was, at least in part, developed by the company’s hacking and surveillance tech division, Trenchant. The two former employees both had knowledge of the company’s iPhone hacking tools. Both spoke on condition of anonymity because they weren’t authorized to talk about their work for the company.
It’s always super interesting to see what malware looks like when it’s created through a professional software development process. And the TechCrunch article has some speculation as to how the US lost control of it. It seems that an employee of L3Harris’s surviellance tech division, Trenchant, sold it to the Russian government.
Tags:
Apple
,
cryptocurrency
,
cybersecurity
,
hacking
,
iOS
,
iPhone
,
malware
,
NSA
,
Russia
Posted on April 2, 2026 at 6:05 AM
•
0 Comments
Is “Hackback” Official US Cybersecurity Strategy?
The 2026 US “
Cyber Strategy for America
” document is mostly the same thing we’ve seen out of the White House for over a decade, but with a more aggressive tone.
But one sentence stood out: “We will unleash the private sector by creating incentives to identify and disrupt adversary networks and scale our national capabilities.” This sounds like a call for hackback: giving private companies permission to conduct offensive cyber operations.
The Economist
noticed
(alternate
link
) this, too.
I think this is an
incredibly dumb idea
:
In warfare, the notion of counterattack is extremely powerful. Going after the enemy­—its positions, its supply lines, its factories, its infrastructure—­is an age-old military tactic. But in peacetime, we call it revenge, and consider it dangerous. Anyone accused of a crime deserves a fair trial. The accused has the right to defend himself, to face his accuser, to an attorney, and to be presumed innocent until proven guilty.
Both vigilante counterattacks, and preemptive attacks, fly in the face of these rights. They punish people before who haven’t been found guilty. It’s the same whether it’s an angry lynch mob stringing up a suspect, the MPAA disabling the computer of someone it believes made an illegal copy of a movie, or a corporate security officer launching a denial-of-service attack against someone he believes is targeting his company over the net.
In all of these cases, the attacker could be wrong. This has been true for lynch mobs, and on the internet it’s even harder to know who’s attacking you. Just because my computer looks like the source of an attack doesn’t mean that it is. And even if it is, it might be a zombie controlled by yet another computer; I might be a victim, too. The goal of a government’s legal system is justice; the goal of a vigilante is expediency.
We don’t issue letters of marque on the high seas anymore; we shouldn’t do it in cyberspace.
Tags:
cybersecurity
,
hackback
,
hacking
,
national security policy
Posted on April 1, 2026 at 12:57 PM
•
7 Comments
A Taxonomy of Cognitive Security
Last week, I listened to a fascinating talk by K. Melton on cognitive security, cognitive hacking, and reality pentesting. The slides from the talk are
here
, but—even better—Menton has a
long essay
laying out the basic concepts and ideas.
The whole thing is important and well worth reading, and I hesitate to excerpt. Here’s a taste:
The NeuroCompiler is where raw sensory data gets interpreted before you’re consciously aware of it. It decides what things mean, and it does this fast, automatic, and mostly invisible. It’s also where the majority of cognitive exploits actually land, right in this sweet spot between perception and conscious thought.
This is my term for
what Daniel Kahneman called System 1 thinking
. If the Sensory Interface is the intake port, the NeuroCompiler is what turns that input into “filtered meaning” before the Mind Kernel ever sees it. It takes raw signal (e.g., photons, sound waves, chemical gradients, pressure) and translates it into something actionable based on binary categories like threat or safe, familiar or novel, trustworthy or suspicious.
The speed is both an evolutionary feature and a modern bug. Processing here is fast enough to get you out of the way of a thrown object before you’ve consciously registered it. But “good enough most of the time” means “predictably wrong some of the time….
A critical architectural feature: the NeuroCompiler can route its output directly back to the Sensory Interface and out as behavior, skipping the conscious awareness of the Mind Kernel
entirely
. Reflex and startle responses use this mechanism, making this bypass pathway enormously useful for survival. Yet it leaves a wide-open backdoor. If the layer that holds access to skepticism
... (truncated)
