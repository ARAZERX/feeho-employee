# Security

FEEHO Employee v0.1 is an alpha contract toolkit. It does not execute a model, but it processes YAML, JSON and filesystem paths from employee packages.

## Report a vulnerability

Email **arazerx@gmail.com** with reproduction steps, affected version and potential impact. Do not include credentials or real customer data. Do not open a public issue for an unpatched vulnerability.

We will acknowledge a report as soon as practical, assess it and coordinate disclosure after a fix is available. No fixed response-time or bounty is promised.

## Supported version

Security fixes are applied to the latest `main` until stable release support policy is published.

## Package safety rules

- YAML is loaded with `yaml.safe_load`.
- Do not load employee packages from untrusted sources without review.
- Exports reject symlinks and unsafe paths.
- Keep model credentials and enterprise data outside the package and outside Git.
