"""Time three Fibonacci calls run in separate threads versus one after another.

Run from this folder with:  python fib_threads.py
"""

import os
import platform
import threading
import time

from fibonacci import fibonacci

FIB_INPUTS = (35, 38, 40)
ROUNDS = 10

RESULT_WIDTH = 13
TIME_WIDTH = 18


class FibCall:
    """One Fibonacci call: its input, its result, and when it started and ended."""

    def __init__(self, n):
        """Create a call for fibonacci(n) that has not run yet."""
        self.n = n
        self.result = None
        self.start_ns = 0
        self.end_ns = 0

    def run(self):
        """Compute fibonacci(n) and record the start and end time in nanoseconds."""
        self.start_ns = time.perf_counter_ns()
        self.result = fibonacci(self.n)
        self.end_ns = time.perf_counter_ns()


def make_calls(inputs):
    """Return a new list of FibCall objects, one per input value."""
    calls = []
    for n in inputs:
        calls.append(FibCall(n))
    return calls


def run_threaded(inputs):
    """Run each call in its own thread and return the finished FibCall list."""
    calls = make_calls(inputs)
    threads = []
    for call in calls:
        # Each thread only writes to its own FibCall object, so no Lock is needed.
        threads.append(threading.Thread(target=call.run))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return calls


def run_sequential(inputs):
    """Run every call one after another in the main thread and return them."""
    calls = make_calls(inputs)
    for call in calls:
        call.run()
    return calls


def total_time_ns(calls):
    """Return T: the latest end time minus the earliest start time.

    For a sequential run this is the end of the last call minus the start
    of the first, so the same function serves both runs.
    """
    earliest_start = calls[0].start_ns
    latest_end = calls[0].end_ns
    for call in calls:
        if call.start_ns < earliest_start:
            earliest_start = call.start_ns
        if call.end_ns > latest_end:
            latest_end = call.end_ns
    return latest_end - earliest_start


def percent_difference(threaded_avg, sequential_avg):
    """Return the threaded average relative to the sequential one, in percent.

    Positive means the threaded run took longer; negative means it was faster.
    The sequential run is the baseline because it is the version without threads.
    """
    return (threaded_avg - sequential_avg) / sequential_avg * 100


def print_table_header(title, inputs):
    """Print the title and the column headings for one run's results table."""
    print(title)
    header = f"{'Round':>5}"
    for n in inputs:
        label = f"fib({n})"
        header += f"  {label:>{RESULT_WIDTH}}"
    header += f"  {'T (ns)':>{TIME_WIDTH}}"
    print(header)
    print("-" * len(header))


def print_round(round_number, calls, total_ns):
    """Print one table row: the round number, the three results and T."""
    row = f"{round_number:>5}"
    for call in calls:
        row += f"  {call.result:>{RESULT_WIDTH},}"
    row += f"  {total_ns:>{TIME_WIDTH},}"
    print(row)


def run_rounds(title, run_function, inputs, rounds):
    """Repeat one kind of run for the given number of rounds and print each round.

    run_function is run_threaded or run_sequential. Returns the list of T values.
    """
    print_table_header(title, inputs)
    totals = []
    for round_number in range(1, rounds + 1):
        calls = run_function(inputs)
        total_ns = total_time_ns(calls)
        totals.append(total_ns)
        print_round(round_number, calls, total_ns)
    print()
    return totals


def print_summary(threaded_totals, sequential_totals):
    """Print the average T of each run and the percentage difference between them."""
    threaded_avg = sum(threaded_totals) / len(threaded_totals)
    sequential_avg = sum(sequential_totals) / len(sequential_totals)
    difference = percent_difference(threaded_avg, sequential_avg)
    print(f"Average T, threaded:   {threaded_avg:>{TIME_WIDTH},.0f} ns")
    print(f"Average T, sequential: {sequential_avg:>{TIME_WIDTH},.0f} ns")
    if difference >= 0:
        print(f"Threaded took {difference:.2f}% longer than sequential.")
    else:
        print(f"Threaded took {-difference:.2f}% less time than sequential.")


def main():
    """Run the threaded and sequential experiments and print the results."""
    print(f"Python {platform.python_version()} on {platform.system()}, "
          f"{os.cpu_count()} logical CPUs")
    print(f"Inputs: n = {FIB_INPUTS}    Rounds: {ROUNDS}")
    print()
    threaded_totals = run_rounds("Threaded run (one thread per call)",
                                 run_threaded, FIB_INPUTS, ROUNDS)
    sequential_totals = run_rounds("Sequential run (main thread only)",
                                   run_sequential, FIB_INPUTS, ROUNDS)
    print_summary(threaded_totals, sequential_totals)


if __name__ == "__main__":
    main()
