Changelog 13/11/25:

secure: refactored backend to remove dotenv/venv dependencies and apply security hardening

- removed .env and python-dotenv usage
- removed virtual environment dependency from project
- rebuilt app/__init__.py with secure configuration, headers, and logging
- added cookie security settings and disabled debug mode
- updated database path for secure environment
- added rotating file logging for monitoring
- ensured instance directory creation
- cleaned up imports and removed unresolved interpreter issues

The secure backend is now simpler, more stable, and aligned with OWASP secure configuration practices.
