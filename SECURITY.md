# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by
[opening a private security advisory](https://github.com/ZviBaratz/gnome-extension-reviewer/security/advisories/new)
on GitHub.

Do not open a public issue for security vulnerabilities.

## Scope

ego-lint processes untrusted extension code. Vulnerabilities include:
- Command injection via crafted filenames or metadata
- Path traversal in file-processing scripts
- Regex denial of service (ReDoS) in pattern rules
