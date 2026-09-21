"""South Korea trading-card worker entrypoint.

This is a separate operational worker path while sharing the tested
CloakBrowser implementation in worker.py. Korean marketplace selectors and
status vocabulary are handled by the common collector.
"""

from worker import main


if __name__ == "__main__":
    main()

