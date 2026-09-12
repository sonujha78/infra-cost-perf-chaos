# CPU Noisy-Neighbor Test — Host-level cgroups v2 (outside Kubernetes)

## Goal
Demonstrate that an unprotected process is starved by a noisy neighbor,
and that cgroup CPU weighting protects it — the same mechanism Kubernetes
uses internally via QoS classes.

## Method
- Used `systemd-run --scope` to launch stress-ng processes directly into
  dedicated transient cgroups (avoids the fork/race issue of manually
  writing PIDs to cgroup.procs after backgrounding a process).
- critical = 1 stress-ng CPU worker (simulates a critical, latency-sensitive process)
- noisy = 48 stress-ng CPU workers on a 12-core host (heavy oversubscription)

## Key finding: isolation alone is not enough
Placing critical and noisy in SEPARATE cgroups with default equal weight
gave critical its full fair share regardless of noisy's thread count —
cgroups v2 does group-level fair scheduling by default, so isolation alone
already provides some protection. To realistically model an *unprotected*
workload (e.g. two pods with no resource weighting), both processes were
placed in the SAME cgroup for the BEFORE test, letting raw per-thread CFS
competition occur.

## BEFORE — critical and noisy in the same (unweighted) cgroup
- critical worker CPU usage: ~37.8% (of a full core) — starved by 48
  competing threads instead of getting close to 100%

## AFTER — critical and noisy in separate cgroups, weighted
- demo-critical-protected: CPUWeight=900
- demo-noisy-limited: CPUWeight=10
- Over a 15s window: critical usage_usec = 15,973,795 (~99.8% of one core)
- Over the same window: noisy usage_usec = 131,790,177 (spread across 48 threads)

## Conclusion
Without cgroup weighting/isolation, a noisy neighbor with many threads can
reduce a critical single-threaded process's CPU share from ~100% to ~38%.
Applying cgroup CPU weights (the same primitive Kubernetes sets under the
hood for QoS classes / resource requests-limits) restores the critical
process to ~100% of its fair share even under heavy contention — proving
the protection mechanism actually works, not just in theory.
