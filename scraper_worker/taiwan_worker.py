"""Taiwan trading-card worker entrypoint.

The regional entrypoint intentionally reuses the hardened browser collector so
pagination, image extraction, status filtering, and JSON output stay exactly
the same as the Japan worker. Taiwan-specific platform aliases and URLs live
in worker.py; this file gives the scheduler its own independently configurable
process path.
"""

from worker import main


if __name__ == "__main__":
    main()

