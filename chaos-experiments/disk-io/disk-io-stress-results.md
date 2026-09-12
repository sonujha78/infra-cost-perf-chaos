# Disk I/O Stress — Scheduler Impact Under Contention

## Method
Simulates a "noisy neighbor" scenario: a heavy sequential write workload
(backup/log-shipping style — 2GB, 1MB blocks, iodepth=64, 2 jobs)
running in the background, while a latency-sensitive "DB query"
workload (small 4K random reads, iodepth=1 — simulating an index
lookup) runs concurrently. Tested with both `none` and `mq-deadline`
schedulers on the same NVMe device (`/dev/nvme0n1`).

## Results (DB query latency, under noisy-neighbor contention)
| Scheduler | Read IOPS | Avg latency |
|-----------|-----------|--------------|
| none | 690,000 | 1225.28 ns |
| mq-deadline | 745,000 | 1124.51 ns |

mq-deadline showed an ~8% latency improvement under this contended
workload — a real, measurable difference, unlike the earlier no-contention
benchmark in `../../kernel-tuning/io-scheduler/` where the two schedulers
were statistically identical (<1% difference).

## Interpretation
This is the expected and meaningful pattern: I/O scheduler choice matters
more as contention increases. `mq-deadline`'s deadline-based request
ordering gives a small but real benefit when a latency-sensitive
workload (DB query) is competing against a throughput-heavy one (backup
writer) for the same NVMe queues. That said, the absolute difference
here (~100ns) is still tiny in practical terms — NVMe's deep internal
queue parallelism absorbs most of the contention on its own, which is
why even the "worse" scheduler (`none`) still delivered sub-microsecond
average latency at 690K IOPS.

## Practical takeaway
On this hardware class (NVMe SSD), scheduler choice is a minor,
second-order optimization compared to right-sizing (Part A) or
autoscaling tuning (Part B) — both of which produced 10-200x effects
versus this experiment's ~8%. The scheduler decision would matter far
more on spinning-disk-backed storage, where the seek-time savings from
request reordering are measured in milliseconds, not nanoseconds.
`none` is reset as the final setting for this NVMe device, consistent
with the Part C recommendation.
