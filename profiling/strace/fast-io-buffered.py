# Fixed: buffer all writes, flush once at the end
with open('/tmp/fast-io-test.txt', 'w') as f:
    buffer = []
    for i in range(5000):
        buffer.append('x')
    f.write(''.join(buffer))   # single write syscall instead of 5000
