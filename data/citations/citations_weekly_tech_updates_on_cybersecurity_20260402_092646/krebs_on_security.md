# Krebs on Security

**Source URL:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Scraped Page:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Title:** Krebs on Security
**Scraped At:** 2026-04-02T09:26:48.203647Z

---

Krebs on Security – In-depth security news and investigation
Advertisement
Advertisement
A financially motivated data theft and extortion group is attempting to inject itself into the Iran war, unleashing a worm that spreads through poorly secured cloud services and wipes data on infected systems that use Iran’s time zone or have Farsi set as the default language.
Experts say the wiper campaign against Iran materialized this past weekend and came from a relatively new cybercrime group known as
TeamPCP
. In December 2025, the group began compromising corporate cloud environments using a self-propagating worm that went after exposed Docker APIs, Kubernetes clusters, Redis servers, and the React2Shell vulnerability. TeamPCP then attempted to move laterally through victim networks, siphoning authentication credentials and extorting victims over Telegram.
A snippet of the malicious CanisterWorm that seeks out and destroys data on systems that match Iran’s timezone or have Farsi as the default language. Image: Aikido.dev.
In a profile of TeamPCP published in January, the security firm
Flare
said the group weaponizes exposed control planes rather than exploiting endpoints, predominantly targeting cloud infrastructure over end-user devices, with Azure (61%) and AWS (36%) accounting for 97% of compromised servers.
“TeamPCP’s strength does not come from novel exploits or original malware, but from the large-scale automation and integration of well-known attack techniques,” Flare’s
Assaf Morag
wrote
. “The group industrializes existing vulnerabilities, misconfigurations, and recycled tooling into a cloud-native exploitation platform that turns exposed infrastructure into a self-propagating criminal ecosystem.”
On March 19, TeamPCP executed a supply chain attack against the vulnerability scanner
Trivy
from
Aqua Security
, injecting credential-stealing malware into official releases on GitHub actions. Aqua Security said it has since
removed
the harmful files, but the security firm Wiz
notes
the attackers were able to publish malicious versions that snarfed SSH keys, cloud credentials, Kubernetes tokens and cryptocurrency wallets from users.
Over the weekend, the same technical infrastructure TeamPCP used in the Trivy attack was leveraged to deploy a new malicious payload which executes a wiper attack if the user’s timezone and locale are determined to correspond to Iran, said
Charlie Eriksen
, a security researcher at
Aikido
. In
a blog post
published on Sunday, Eriksen said if the wiper component detects that the victim is in Iran and has access to a Kubernetes cluster, it will destroy data on every node in that cluster.
“If it doesn’t it will just wipe the local machine,” Eriksen told KrebsOnSecurity.
Image: Aikido.dev.
Continue reading
→
The U.S. Justice Department joined authorities in Canada and Germany in dismantling the online infrastructure behind four highly disruptive botnets that compromised more than three million Internet of Things (IoT) devices, such as routers and web cameras. The feds say the four botnets — named
Aisuru
,
Kimwolf
,
JackSkid
and
Mossad
— are responsible for a series of recent record-smashing distributed denial-of-service (DDoS) attacks capable of knocking nearly any target offline.
Image: Shutterstock, @Elzicon.
The Justice Department said the Department of Defense Office of Inspector General’s (DoDIG)
Defense Criminal Investigative Service
(DCIS) executed seizure warrants targeting multiple U.S.-registered domains, virtual servers, and other infrastructure involved in DDoS attacks against Internet addresses owned by the DoD.
The government alleges the unnamed people in control of the four botnets used their crime machines to launch hundreds of thousands of DDoS attacks, often demanding extortion payments from victims. Some victims reported tens of thousands of dollars in losses and remediation expenses.
The oldest of the botnets — Aisuru — issued more than 200,000 attacks commands, while JackSkid hurled at least 90,000 attacks. Kimwolf issued more than 25,000 attack commands, the government said, while Mossad was blamed for roughy 1,000 digital sieges.
The DOJ
said
the law enforcement action was designed to prevent further infection to victim devices and to limit or eliminate the ability of the botnets to launch future attacks. The case is being investigated by the DCIS with help from the FBI’s field office in Anchorage, Alaska, and the DOJ’s statement credits nearly two dozen technology companies with assisting in the operation.
Continue reading
→
Advertisement
A hacktivist group with links to Iran’s intelligence agencies is claiming responsibility for a data-wiping attack against
Stryker
, a global medical technology company based in Michigan. News reports out of Ireland, Stryker’s largest hub outside of the United States, said the company sent home more than 5,000 workers there today. Meanwhile, a voicemail message at Stryker’s main U.S. headquarters says the company is currently experiencing a building emergency.
Based in Kalamazoo, Michigan, Stryker [NYSE:SYK] is a medical and surgical equipment maker that reported $25 billion in global sales last year. In a lengthy statement posted to Telegram, a hacktivist group known as
Handala
(a.k.a. Handala Hack Team) claimed that Stryker’s offices in 79 countries have been forced to shut down after the group erased data from more than 200,000 systems, servers and mobile devices.
A manifesto posted by the Iran-backed hacktivist group Handala, claiming a mass data-wiping attack against medical technology maker Stryker.
“All the acquired data is now in the hands of the free people of the world, ready to be used for the true advancement of humanity and the exposure of injustice and corruption,” a portion of the Handala statement reads.
The group said the wiper attack was in retaliation for a Feb. 28 missile strike that hit an Iranian school and killed at least 175 people, most of them children.
The New York Times
reports
today
... (truncated)
