# Security Policy

## Reporting Vulnerabilities

**DO NOT** open public GitHub issues for security vulnerabilities.

📧 Email: security@mltoolkit.com
🔒 PGP Key: [keyserver link]
⏱️ Response time: 48 hours

## Security Measures

| Layer | Measure | Status |
|-------|---------|--------|
| API | JWT Authentication | ✅ |
| API | Rate Limiting | ✅ |
| API | Input Validation | ✅ |
| Infrastructure | Non-root Docker | ✅ |
| Infrastructure | Read-only containers | ✅ |
| Code | Bandit scanning | ✅ |
| Dependencies | Safety scanning | ✅ |
| CI/CD | Automated security scans | ✅ |
| Secrets | Environment variables only | ✅ |
| Models | SHA256 integrity check | ✅ |

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x | ✅ Active |
