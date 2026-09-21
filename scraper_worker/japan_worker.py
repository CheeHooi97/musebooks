"""Dedicated Japan marketplace worker entrypoint.

The collector implementation remains shared with the generic worker, but this
entrypoint is launched in its own Python/Chromium process and worker lane.
"""

from worker import main


if __name__ == "__main__":
    main()
