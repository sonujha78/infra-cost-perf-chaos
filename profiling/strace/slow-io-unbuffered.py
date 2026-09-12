# Deliberately inefficient: writes + flushes 1 byte at a time (5000 times)
# instead of buffering — simulates a common real-world bug where an app
# doesn't batch its I/O.
with open('/tmp/slow-io-test.txt', 'w') as f:
    for i in range(5000):
        f.write('x')
        f.flush()   # forces a syscall every single write — the bug
