# bpftrace — Live eBPF Tracing

## One-liner 1: syscall count by process (10s window)
    sudo timeout 10 bpftrace -e '
    tracepoint:raw_syscalls:sys_enter
    {
        @syscalls[comm] = count();
    }
    '

Ran on a live system with the full kind cluster + Prometheus/Grafana +
this project's load generators running. Top consumers (full output in
`syscall-count-output.txt`):

    kubelet:            82356
    containerd-shim:     47014
    upowerd:             43923
    coredns:             35739
    containerd:          34225
    kube-apiserver:      26576
    udev-worker:         22971
    wget:                66102   <- this project's own bursty load generator

This is a live, per-process breakdown of exactly what's consuming
syscall time system-wide — useful for spotting an unexpectedly
syscall-heavy process without attaching to it individually first.

## One-liner 2: disk I/O latency histogram (15s window)
    sudo timeout 15 bpftrace -e '
    tracepoint:block:block_rq_issue
    {
        @start[args.dev, args.sector] = nsecs;
    }
    tracepoint:block:block_rq_complete
    {
        if (@start[args.dev, args.sector]) {
            @latency_us = hist((nsecs - @start[args.dev, args.sector]) / 1000);
            delete(@start[args.dev, args.sector]);
        }
    }
    '

Note: an earlier attempt used `kprobe:blk_account_io_start` /
`kprobe:blk_account_io_done`, which failed with "not traceable (either
non-existing, inlined, or marked as notrace)" on this kernel (7.0.0-31)
— those functions got inlined and are no longer stable kprobe targets.
Switched to the `block:block_rq_issue` / `block:block_rq_complete`
tracepoints instead, which are part of the kernel's stable ABI and
don't break across kernel versions the way raw kprobes on internal
functions can.

Generated load with `dd if=/dev/zero of=/tmp/io-test-file bs=1M
count=200 oflag=direct` (200MB, measured at 3.3 GB/s — confirms this is
an NVMe SSD). Result histogram in `disk-io-latency-histogram.txt`:
most requests completed in 32-64µs, with a secondary cluster in the
512µs-2ms range (likely queueing effects from many parallel requests at
that throughput).

## Why this matters
This is the exact workflow used to validate an I/O scheduler choice
under real load (see `../../kernel-tuning/io-scheduler/`): without a
tool like this, "is the scheduler actually helping?" is a guess. With
it, it's a measured before/after latency distribution.
