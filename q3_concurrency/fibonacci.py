"""Naive recursive Fibonacci, used as the CPU-heavy workload in Q3."""


def fibonacci(n):
    """Return the n-th Fibonacci number, with fibonacci(0) = 0 and fibonacci(1) = 1.

    n must be a non-negative int. This is the plain recursive definition
    with no memoisation, on purpose: the experiment needs a function that
    keeps the CPU busy. The number of calls for input n is 2 * F(n + 1) - 1,
    which grows exponentially (O(2^n) as an upper bound).

    Primitive operations per call:
      base case (n <= 1): 1 comparison + 1 return
      otherwise:          1 comparison + 2 subtractions + 2 calls
                          + 1 addition + 1 return
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
