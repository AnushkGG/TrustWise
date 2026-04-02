# Schneier on Security

**Source URL:** [https://www.schneier.com/](https://www.schneier.com/)
**Scraped Page:** [https://www.schneier.com/](https://www.schneier.com/)
**Title:** Schneier on Security
**Scraped At:** 2026-04-02T09:12:04.569322Z

---

Schneier on Security -
Search
Powered by
DuckDuckGo
Blog
Essays
Whole site
Subscribe
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
6 Comments
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
. Reflex and startle responses use this mechanism, making this bypass pathway enormously useful for survival. Yet it leaves a wide-open backdoor. If the layer that holds access to skepticism and deliberate evaluation can be bypassed completely, a host of exploits become possible that would otherwise fail.
That’s just one of the five levels Melton talks about: sensory interface, neurocompiler, mind kernel, the mesh, and cultural substrate.
Melton’s taxonomy is compelling, and her parallels to IT systems are fascinating. I have long said that a genius idea is one that’s incredibly obvious once you hear it, but one that no one has said before. This is the first time I’ve heard cognition described in this way.
Tags:
security analysis
,
social engineering
,
taxonomies
Posted on April 1, 2026 at 5:59 AM
•
4 Comments
Inventors of Quantum Cryptography Win Turing Award
Charles Bennett and Gilles Brassard have
won
the 2026 Turing Award for inventing quantum cryptography.
I am incredibly pleased to see them get this recognition. I have always thought the technology to be fantastic, even though I think it’s largely unnecessary. I wrote up my thoughts back in 2008, in an
essay
titled “Quantum Cryptography: As Awesome As It Is Pointless.”
Back then, I wrote:
While I like the science of quantum cryptography—my undergraduate degree was in physics—I don’t see any commercial value in it. I don’t believe it solves any security problem that needs solving. I don’t believe that it’s worth paying for, and I can’t imagine anyone but a few technophiles buying and deploying it. Systems that use it don’t magically become unbreakable, because the quantum part doesn’t address the weak points of the system.
Security is a chain; it’s as strong as the weakest link. Mathematical cryptography, as bad as it sometimes is, is the strongest link in most security chains. Our symmetric and public-key algorithms are pretty good, even though they’re not based on much rigorous mathematical theory. The real problems are elsewhere: computer security, network security, user interface and so on.
Cryptography is the one area of security that we can get right. We already have good encryption algorithms, good authentication algorithms and good key-agreement
... (truncated)
