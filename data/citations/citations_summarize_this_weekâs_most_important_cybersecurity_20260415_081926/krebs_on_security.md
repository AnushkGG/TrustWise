# Krebs on Security

**Source URL:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Scraped Page:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Title:** Krebs on Security
**Scraped At:** 2026-04-15T08:19:44.290476Z

---

Krebs on Security – In-depth security news and investigation
Advertisement
Advertisement
Microsoft
today pushed software updates to fix a staggering 167 security vulnerabilities in its
Windows
operating systems and related software, including a
SharePoint Server
zero-day and a publicly disclosed weakness in
Windows Defender
dubbed “
BlueHammer
.” Separately,
Google Chrome
fixed its fourth zero-day of 2026, and an emergency update for
Adobe Reader
nixes an actively exploited flaw that can lead to remote code execution.
Redmond warns that attackers are already targeting
CVE-2026-32201
, a vulnerability in Microsoft SharePoint Server that allows attackers to spoof trusted content or interfaces over a network.
Mike Walters
, president and co-founder of
Action1
, said CVE-2026-32201 can be used to deceive employees, partners, or customers by presenting falsified information within trusted SharePoint environments.
“This CVE can enable phishing attacks, unauthorized data manipulation, or social engineering campaigns that lead to further compromise,” Walters said. “The presence of active exploitation significantly increases organizational risk.”
Microsoft also addressed BlueHammer (
CVE-2026-33825
), a privilege escalation bug in Windows Defender. According to BleepingComputer, the researcher who discovered the flaw
published exploit code for it
after notifying Microsoft and growing exasperated with their response.
Will Dormann
, senior principal vulnerability analyst at
Tharros
, says he
confirmed
that the public BlueHammer exploit code no longer works after installing today’s patches.
Continue reading
→
Hackers linked to Russia’s military intelligence units are using known flaws in older Internet routers to mass harvest authentication tokens from
Microsoft Office
users, security experts warned today. The spying campaign allowed state-backed Russian hackers to quietly siphon authentication tokens from users on more than 18,000 networks without deploying any malicious software or code.
Microsoft said in
a blog post
today it identified more than 200 organizations and 5,000 consumer devices that were caught up in a stealthy but remarkably simple spying network built by a Russia-backed threat actor known as “
Forest Blizzard
.”
How targeted DNS requests were redirected at the router. Image: Black Lotus Labs.
Also known as
APT28
and Fancy Bear, Forest Blizzard is attributed to the military intelligence units within Russia’s General Staff Main Intelligence Directorate (GRU). APT 28 famously compromised the Hillary Clinton campaign, the Democratic National Committee, and the Democratic Congressional Campaign Committee in 2016 in an attempt to interfere with the U.S. presidential election.
Researchers at
Black Lotus Labs
, a security division of the Internet backbone provider
Lumen
, found that at the peak of its activity in December 2025, Forest Blizzard’s surveillance dragnet ensnared more than 18,000 Internet routers that were mostly unsupported, end-of-life routers, or else far behind on security updates. A
new report
from Lumen says the hackers primarily targeted government agencies—including ministries of foreign affairs, law enforcement, and third-party email providers.
Black Lotus Security Engineer
Ryan English
said the GRU hackers did not need to install malware on the targeted routers, which were mainly older
Mikrotik
and
TP-Link
devices marketed to the Small Office/Home Office (SOHO) market. Instead, they used known vulnerabilities to modify the Domain Name System (DNS) settings of the routers to include DNS servers controlled by the hackers.
As the U.K.’s
National Cyber Security Centre
(NCSC) notes in
a new advisory
detailing how Russian cyber actors have been compromising routers, DNS is what allows individuals to reach websites by typing familiar addresses, instead of associated IP addresses. In a DNS hijacking attack, bad actors interfere with this process to covertly send users to malicious websites designed to steal login details or other sensitive information.
English said the routers attacked by Forest Blizzard were reconfigured to use DNS servers that pointed to a handful of virtual private servers controlled by the attackers. Importantly, the attackers could then propagate their malicious DNS settings to all users on the local network, and from that point forward intercept any
OAuth authentication tokens
transmitted by those users.
Continue reading
→
Advertisement
An elusive hacker who went by the handle “
UNKN
” and ran the early Russian ransomware groups
GandCrab
and
REvil
now has a name and a face. Authorities in Germany say 31-year-old Russian
Daniil Maksimovich Shchukin
headed both cybercrime gangs and helped carry out at least 130 acts of computer sabotage and extortion against victims across the country between 2019 and 2021.
Shchukin was named as UNKN (a.k.a. UNKNOWN) in
an advisory
published by the
German Federal Criminal Police
(the “Bundeskriminalamt” or BKA for short). The BKA said Shchukin and another Russian — 43-year-old
Anatoly Sergeevitsch Kravchuk
— extorted nearly $2 million euros across two dozen cyberattacks that caused more than 35 million euros in total economic damage.
Daniil Maksimovich SHCHUKIN, a.k.a. UNKN, and Anatoly Sergeevitsch Karvchuk, alleged leaders of the GandCrab and REvil ransomware groups.
Germany’s BKA said Shchukin acted as the head of one of the largest worldwide operating ransomware groups GandCrab and REvil, which pioneered the practice of double extortion — charging victims once for a key needed to unlock hacked systems, and a separate payment in exchange for a promise not to publish stolen data.
Shchukin’s name appeared in a
Feb. 2023 filing
(PDF) from the U.S. Justice Department seeking the seizure of various cryptocurrency accounts associated with proceeds from the REvil ransomware gang’s activities. The government said the digital wallet tied to Shchukin contained more than $317,000 in ill-gotten cryptocurrency.
The GandCrab ransomwa
... (truncated)
