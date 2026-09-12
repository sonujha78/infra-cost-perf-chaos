# sysctl Network & Memory Tuning

Config file: `/etc/sysctl.d/99-production-tuning.conf` (see `99-production-tuning.conf`
in this directory — a copy of the applied file for reference)

## Parameters Tuned

| Parameter | Before | After | Problem it Fixes |
|-----------|--------|-------|-------------------|
| `net.core.somaxconn` | 4096 | 65535 | Connection backlog queue — demonstrated below |
| `net.ipv4.tcp_tw_reuse` | 2 (loopback-only) | 1 (global) | Ephemeral port exhaustion from TIME_WAIT sockets |
| `net.ipv4.ip_local_port_range` | 32768-60999 (~28K ports) | 2000-65000 (~63K ports) | Outbound connection port exhaustion under high concurrency |
| `vm.swappiness` | 60 | 10 | Swap-induced latency spikes on memory pressure |

## Demonstrated: somaxconn backlog exhaustion

Ran a deliberately slow TCP server (accepts connections only after a 15s
delay) with two different `listen()` backlog values, then fired 50 rapid
connection attempts against each:

| Backlog | Successful Connections | Refused Connections |
|---------|--------------------------|------------------------|
| 5       | 6                        | 44                     |
| 100     | 50                       | 0                      |

This is the exact failure mode `net.core.somaxconn` controls in
production: if the kernel's connection backlog is too small, a burst of
concurrent client connections gets refused (ECONNREFUSED) even though the
server process is healthy and would have processed them if the OS had
queued them.

## vm.swappiness — cross-reference

This was also demonstrated experimentally (not just theoretically) in
`../cgroups/memory-oom-demo.md`: with default host swap settings, a
cgroup-memory-limited process avoided OOM-kill entirely by having its
anonymous pages swapped out instead — silently degrading to disk-speed
memory access rather than failing fast. Lowering `vm.swappiness` makes
the kernel prefer reclaiming page cache over swapping application
memory, which is the right tradeoff for latency-sensitive DB/cache nodes.

## Addendum: fs.inotify — found via a real failure, not planning

While installing Chaos Mesh for Part 5, `chaos-controller-manager` crashed
with `unable to start manager {"error": "too many open files"}`. This
tied directly back to the same OS-level symptom noted earlier in
`../cgroups/README.md` ("Failed to allocate directory watch") — both are
`fs.inotify` limit exhaustion, not a file-descriptor (`nofile`) ulimit
issue.

| Parameter | Before | After |
|-----------|--------|-------|
| fs.inotify.max_user_watches | 65536 | 524288 |
| fs.inotify.max_user_instances | 128 | 512 |

Kubernetes controllers (Chaos Mesh's controller-manager included) watch
large numbers of Kubernetes resources via the client-go informer
framework, which relies on inotify-style watches under the hood at
scale. The Ubuntu default of 65536 watches / 128 instances is tuned for
desktop use, not for running multiple watch-heavy controllers alongside
a full kind cluster, Prometheus, KEDA, and VPA on the same host.

This is a real example of the task's point about kernel tuning: the
fix wasn't planned in advance — it was found by hitting an actual
production-style failure and diagnosing it via `kubectl logs`, not by
copying a generic sysctl checklist.
