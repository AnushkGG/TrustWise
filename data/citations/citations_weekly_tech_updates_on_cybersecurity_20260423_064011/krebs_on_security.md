# Krebs on Security

**Source URL:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Scraped Page:** [https://krebsonsecurity.com/](https://krebsonsecurity.com/)
**Title:** Krebs on Security
**Scraped At:** 2026-04-23T06:40:22.728467Z

---

Krebs on Security – In-depth security news and investigation
Advertisement
Advertisement
A 24-year-old British national and senior member of the cybercrime group “
Scattered Spider
” has pleaded guilty to wire fraud conspiracy and aggravated identity theft.
Tyler Robert Buchanan
admitted his role in a series of text-message phishing attacks in the summer of 2022 that allowed the group to hack into at least a dozen major technology companies and steal tens of millions of dollars worth of cryptocurrency from investors.
Buchanan’s hacker handle “
Tylerb
” once graced a leaderboard in the English-language criminal hacking scene that tracked the most accomplished cyber thieves. Now in U.S. custody and awaiting sentencing, the Dundee, Scotland native is facing the possibility of more than 20 years in prison.
Two photos published in a Daily Mail story dated May 3, 2025 show Buchanan as a child (left) and as an adult being detained by airport authorities in Spain. “M&S” in this screenshot refers to Marks & Spencer, a major U.K. retail chain that suffered a ransomware attack last year at the hands of Scattered Spider.
Scattered Spider is the name given to a prolific English-speaking cybercrime group known for using social engineering tactics to break into companies and steal data for ransom, often impersonating employees or contractors to deceive IT help desks into granting access.
As part of his guilty plea, Buchanan admitted conspiring with other Scattered Spider members to launch tens of thousands of SMS-based phishing attacks in 2022 that led to intrusions at a number of technology companies, including Twilio, LastPass, DoorDash, and Mailchimp.
The group then used data stolen in those breaches to carry out
SIM-swapping attacks
that siphoned funds from individual cryptocurrency investors. In an unauthorized SIM-swap, crooks transfer the target’s phone number to a device they control and intercept any text messages or phone calls to the victim’s device — such as one-time passcodes for authentication and password reset links sent via SMS. The U.S. Justice Department
said
Buchanan admitted to stealing at least $8 million in virtual currency from individual victims throughout the United States.
Continue reading
→
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
Advertisement
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
detailing how Russian cyber actors have been compromising routers, DNS is what allows individuals to reach websites by typing familiar addresses, inste
... (truncated)
