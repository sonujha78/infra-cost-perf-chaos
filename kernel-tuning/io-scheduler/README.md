# I/O Scheduler — none vs mq-deadline on NVMe SSD

## Device
`/dev/nvme0n1` — WD PC SN740, 476.9GB, ROTA=0 (non-rotational, confirmed SSD).
Available schedulers: `none`, `mq-deadline` (no `bfq` — not commonly loaded
for NVMe multi-queue devices by default).

## Benchmark
`fio`, simulating a database-like mixed workload:
    --rw=randrw --rwmixread=70 --bs=4k --iodepth=32 --numjobs=4
    --runtime=20 --time_based --direct=1

## Results
| Metric | none (baseline) | mq-deadline | Difference |
|--------|-------------------|--------------|------------|
| Read IOPS | 1,779,000 | 1,769,000 | -0.6% |
| Read avg latency | 1086.77 ns | 1084.19 ns | negligible |
| Write IOPS | 762,000 | 758,000 | -0.5% |
| Write avg latency | 1954.48 ns | 1956.50 ns | negligible |
| CPU sys% | 75.85% | 75.44% | negligible |

Full raw output: `fio-results-none.txt`, `fio-results-mq-deadline.txt`

## Conclusion: use `none` for this NVMe SSD
The benchmark shows `none` and `mq-deadline` perform statistically
identically on this NVMe device (<1% difference, within normal run-to-run
noise). This is the expected and correct result, not a flaw in the test:

- NVMe SSDs are internally massively parallel (thousands of hardware
  queues) and have negligible seek cost — there is no "rotational
  latency" or "head movement" for a software scheduler to optimize
  around.
- `mq-deadline` exists to enforce per-request deadlines and do some I/O
  merging/reordering — useful on devices where request *ordering*
  matters for physical seek time. On NVMe, that reordering work is pure
  CPU overhead with no corresponding benefit, since the drive itself
  handles queuing far more effectively than the kernel scheduler could.
- `none` (a no-op scheduler that passes requests straight to the block
  layer's multi-queue dispatch) is the standard recommendation for NVMe
  because it minimizes CPU overhead per I/O with zero downside on this
  class of hardware.

## When to use something else
- **Spinning disks (HDDs, ROTA=1)**: `mq-deadline` (or the older `bfq`
  for desktop/interactive fairness) matters a lot here, because seek
  time is real and expensive (milliseconds, not nanoseconds) —
  reordering requests to minimize head movement (elevator algorithm)
  gives a measurable throughput and latency win.
- **`bfq`**: optimizes for fairness between multiple competing
  processes/cgroups on a single slow device (e.g. a desktop doing a
  large file copy while also trying to stay responsive). Its extra
  bookkeeping overhead is wasted on a fast NVMe drive where there's
  rarely meaningful queuing contention to arbitrate.
- **A busy database or cache node specifically on HDD-backed storage**
  (still common in cost-sensitive cloud tiers) is exactly where this
  choice would show a real, measurable difference — this NVMe result
  demonstrates the *absence* of that effect on modern SSD hardware,
  which is itself the useful finding: don't spend tuning effort on
  scheduler choice for NVMe-backed nodes; spend it elsewhere (e.g. the
  sysctl/cgroups work in this project).
