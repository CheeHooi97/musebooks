import unittest
from unittest.mock import patch
from photobook_worker import NavigationRateLimiter
from source_navigation import SourceNavigationLimiters


class SourceNavigationTests(unittest.TestCase):
    def test_new_batch_waits_for_the_same_sources_remaining_interval(self):
        limiters = SourceNavigationLimiters(NavigationRateLimiter)
        source = dict(id='source-a', ratePerMinute=6)
        with patch('time.monotonic', side_effect=[100, 100, 104, 110]), patch('time.sleep') as sleep:
            limiters(source, {}).wait()
            limiters(source, {}).wait()
        sleep.assert_called_once_with(6)

    def test_other_platform_starts_independently(self):
        limiters = SourceNavigationLimiters(NavigationRateLimiter)
        with patch('time.monotonic', return_value=100), patch('time.sleep') as sleep:
            limiters(dict(id='source-a', ratePerMinute=6), {}).wait()
            limiters(dict(id='source-b', ratePerMinute=6), {}).wait()
        sleep.assert_not_called()

    def test_stricter_job_delay_does_not_reset_the_previous_navigation_time(self):
        limiters = SourceNavigationLimiters(NavigationRateLimiter)
        source = dict(id='source-a', ratePerMinute=6)
        with patch('time.monotonic', side_effect=[100, 100, 104, 115]), patch('time.sleep') as sleep:
            limiters(source, {}).wait()
            limiters(source, dict(minDelayMs=15000)).wait()
        sleep.assert_called_once_with(11)


if __name__ == '__main__':
    unittest.main()
