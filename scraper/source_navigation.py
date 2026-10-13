"""Keep source navigation timing across separate page-sized collection jobs."""


class SourceNavigationLimiters:
    def __init__(self, factory):
        self.factory = factory
        self.limiters = {}

    def __call__(self, source, request):
        source_id = source['id']
        proposed = self.factory(source, request)
        if source_id not in self.limiters:
            self.limiters[source_id] = proposed
        else:
            limiter = self.limiters[source_id]
            limiter.interval = max(limiter.interval, proposed.interval)
        return self.limiters[source_id]
