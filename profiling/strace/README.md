# strace -c: Finding a Real I/O Bottleneck

## The bug
A Python script writes 5000 bytes to a file, one byte at a time, calling
`flush()` after every single write — forcing a syscall per byte instead
of letting the OS buffer batch them. This is a real, common
anti-pattern: code that "flushes for safety" without realizing the cost.

    with open('/tmp/slow-io-test.txt', 'w') as f:
        for i in range(5000):
            f.write('x')
            f.flush()   # forces a syscall every single write

## Diagnosis: strace -c
    strace -c python3 slow-io-unbuffered.py

Result (see `strace-before-unbuffered.txt`):
    % time   calls   syscall
    86.62%   5000    write
    100.00%  5424    total

`write` alone accounts for 86.62% of all syscall time and 5000 of the
5424 total syscalls — an immediate, unambiguous signal of where the
bottleneck is, found in seconds without guessing.

## The fix
Buffer everything in memory, issue a single `write()`:

    with open('/tmp/fast-io-test.txt', 'w') as f:
        buffer = []
        for i in range(5000):
            buffer.append('x')
        f.write(''.join(buffer))   # single write syscall

## Result: strace -c after the fix
    % time   calls   syscall
    1.33%    1       write
    100.00%  425     total

## Before / After Summary
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| `write` syscalls | 5000 | 1 | 5000x fewer |
| `write` time | 8763µs (86.6% of total) | 52µs (1.3% of total) | ~168x faster |
| Total syscall time | 10117µs | 3897µs | ~2.6x faster |
| Wall-clock time (`time` cmd) | 38ms | 12ms | ~3.2x faster |

## Why this matters
This is the same class of bug that shows up in production as "the app
is slow but CPU usage is low" — the process is spending its time
blocked on syscalls (I/O), not computing. `strace -c` finds this in
seconds by ranking syscalls by time spent, which is exactly the
workflow a production engineer uses before reaching for heavier tools
like perf or bpftrace.
