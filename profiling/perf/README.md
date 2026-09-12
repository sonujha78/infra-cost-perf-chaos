# perf top: Finding a CPU Hotspot

## The bug
Naive prime-checking that checks divisibility all the way up to n
instead of stopping at sqrt(n):

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, n):   # BUG: should stop at sqrt(n)
            if n % i == 0:
                return False
        return True

## Diagnosis: perf top
Ran the script in the background and attached `perf top -p <pid>`:

    sudo perf top -p $CPU_PID -d 2 --stdio

Result:
    53.74%  python3.14  [.] _PyEval_EvalFrameDefault   # interpreter loop itself
    15.40%  python3.14  [.] PyLong_FromLong             # integer object creation
    10.16%  python3.14  [.] _Py_Dealloc                 # integer object destruction
     9.14%  python3.14  [.] PyNumber_Remainder           # the actual `n % i` check

The high `PyLong_FromLong`/`_Py_Dealloc`/`PyNumber_Remainder` percentages
point directly at a tight loop doing enormous numbers of modulo checks
and integer allocations — the fingerprint of an O(n) loop that should be
O(sqrt(n)).

## The fix
    for i in range(2, int(math.sqrt(n)) + 1):   # stop at sqrt(n)

## Before / After
| Metric | Before (O(n)) | After (O(sqrt(n))) | Improvement |
|--------|----------------|------------------------|-------------|
| Wall-clock time | 35.573s | 0.175s | **~203x faster** |
| Result correctness | 17984 primes | 17984 primes | identical (correctness preserved) |

## Why this matters
`perf top` finds *where in the code* CPU time is going at the function
level — without needing to add any instrumentation or guess. Here the
elevated time in `PyNumber_Remainder` (the modulo operator) combined
with the sheer volume of interpreter loop time was the signal that led
straight to the fix: an algorithm doing far more work per input than
necessary. This complements strace (which finds I/O/syscall-bound
bottlenecks) — perf finds CPU-bound ones.
