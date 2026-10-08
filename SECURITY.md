# Security Policy

This pre-alpha project is not ready for high-impact authorization decisions or untrusted production workloads.

Report suspected vulnerabilities through the repository's private security-advisory
form. Do not open a public issue containing exploit details, credentials, or user
data. If private reporting is unavailable, contact the package owner through the
maintainer controls on PyPI before sharing technical details.

Remote backends may transmit wrapped semantic state outside the process. Applications must disclose and configure that behavior explicitly. Never commit provider credentials; use environment-based or secure runtime configuration.
