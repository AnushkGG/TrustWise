# Security policy

## Supported versions

Security fixes are applied to the **default development branch** (typically `main` or the repository’s primary branch). Older branches or tags may not receive backports unless documented elsewhere.

## Reporting a vulnerability

**Please do not** open a public GitHub issue for undisclosed security vulnerabilities.

Preferred options:

1. Use **GitHub Security Advisories** for this repository (if enabled): *Security* tab → *Report a vulnerability*.
2. Or contact the maintainers privately. Replace the placeholder below with a project-specific email or process when available:

   - **Contact:** `security@example.com` (placeholder—update in fork or upstream)

Include:

- A short description of the issue and affected components.
- Steps to reproduce or a proof-of-concept **without** posting live secrets.
- Your assessment of impact (optional).

Maintainers will acknowledge receipt when possible and coordinate a fix and disclosure timeline.

## Expectations

- **No secrets in issues or PRs.** Never paste API keys, `.env` contents, or session tokens. Rotate any credential that was exposed.
- **Responsible disclosure:** Avoid public exploit detail until maintainers have had time to patch.
- **Scope:** Reports should concern this repository’s code and documented deployment patterns. Third-party service policies (cloud LLM providers, etc.) follow those vendors’ programs.

## Secrets and configuration

- Use a **local** `.env` (gitignored). Copy from [.env.example](.env.example).
- Rotate keys that appear in chat logs, CI logs, or accidental commits.
