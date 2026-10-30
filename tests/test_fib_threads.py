"""Tests for q3_concurrency/fib_threads.py, using small n so they run quickly."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q3_concurrency"))

from fib_threads import (FibCall, percent_difference, run_sequential,
                         run_threaded, total_time_ns)

SMALL_INPUTS = (10, 12, 15)
SMALL_RESULTS = [55, 144, 610]


def make_timed_call(start_ns, end_ns):
    """Return a FibCall with hand-set times, for testing total_time_ns."""
    call = FibCall(1)
    call.start_ns = start_ns
    call.end_ns = end_ns
    return call


class TestRuns(unittest.TestCase):
    """Both runs should return correct results with sensible timings."""

    def check_calls(self, calls):
        """Check inputs, results and start <= end for each call."""
        self.assertEqual(len(calls), 3)
        for i in range(len(calls)):
            self.assertEqual(calls[i].n, SMALL_INPUTS[i])
            self.assertEqual(calls[i].result, SMALL_RESULTS[i])
            self.assertLessEqual(calls[i].start_ns, calls[i].end_ns)

    def test_threaded_results(self):
        """The threaded run returns the correct result for each input."""
        self.check_calls(run_threaded(SMALL_INPUTS))

    def test_sequential_results(self):
        """The sequential run returns the correct result for each input."""
        self.check_calls(run_sequential(SMALL_INPUTS))

    def test_sequential_calls_do_not_overlap(self):
        """In the sequential run each call starts after the previous one ends."""
        calls = run_sequential(SMALL_INPUTS)
        for i in range(1, len(calls)):
            self.assertGreaterEqual(calls[i].start_ns, calls[i - 1].end_ns)


class TestTotalTime(unittest.TestCase):
    """T is the latest end minus the earliest start."""

    def test_overlapping_calls(self):
        """Overlapping calls: T spans from the first start to the last end."""
        calls = [make_timed_call(100, 400),
                 make_timed_call(150, 900),
                 make_timed_call(120, 300)]
        self.assertEqual(total_time_ns(calls), 800)

    def test_back_to_back_calls(self):
        """Back-to-back calls: T is the sum of the three durations."""
        calls = [make_timed_call(0, 10),
                 make_timed_call(10, 30),
                 make_timed_call(30, 60)]
        self.assertEqual(total_time_ns(calls), 60)


class TestPercentDifference(unittest.TestCase):
    """Positive means threaded was slower, negative means it was faster."""

    def test_threaded_slower(self):
        """Threaded 110 vs sequential 100 is +10%."""
        self.assertAlmostEqual(percent_difference(110, 100), 10.0)

    def test_threaded_faster(self):
        """Threaded 75 vs sequential 100 is -25%."""
        self.assertAlmostEqual(percent_difference(75, 100), -25.0)

    def test_equal(self):
        """Equal averages give 0%."""
        self.assertAlmostEqual(percent_difference(100, 100), 0.0)


if __name__ == "__main__":
    unittest.main()
