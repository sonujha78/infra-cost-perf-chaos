# cgroups v2 — Manual CPU Limiting (Outside Kubernetes)

## What this demonstrates
Kubernetes sets pod CPU limits by writing to the cgroup v2 `cpu.max`
file for that pod's cgroup. This demo does the same thing manually via
`systemd-run --scope -p CPUQuota=X%`, to show what's actually happening
under the hood when a pod's `resources.limits.cpu` is set.

## Test 1 — No effective limit (CPUQuota=100% = 1 full core)
    sudo systemd-run --scope --unit=cpu-demo-unlimited -p CPUQuota=100% \
      bash -c 'yes > /dev/null & sleep 5; echo done'

Result: `yes` process measured at **100% CPU** — fully consuming one core,
unrestricted.

## Test 2 — CPUQuota=10%
    sudo systemd-run --scope --unit=cpu-demo-limited -p CPUQuota=10% \
      bash -c 'yes > /dev/null & sleep 5; echo done'

Result: `yes` process measured at **9.7% CPU** — the kernel scheduler
throttled it to match the cgroup's CPU quota almost exactly.

## Why this matters for Kubernetes
When a pod spec sets `resources.limits.cpu: "200m"`, kubelet translates
that into a cgroup v2 `cpu.max` value (200m = 20% of one core = quota
20000, period 100000 in cgroup terms) on that container's cgroup. The
kernel CFS (Completely Fair Scheduler) bandwidth controller then throttles
the container's processes exactly like it throttled `yes` here — no
magic, just the same cgroup mechanism Kubernetes automates.

## Side finding: inotify watch limit
Both test runs printed:
    Failed to allocate directory watch: Too many open files

This is `systemd-run`/`systemctl` failing to set up an inotify watch —
an OS-level file-descriptor/inotify-instance limit, not a cgroup issue.
This becomes directly relevant in the ulimits section of this task,
where the same class of "too many open files" failure is diagnosed and
fixed properly (raising `fs.inotify.max_user_watches` /
`fs.inotify.max_user_instances` via sysctl, and nofile ulimits via
systemd unit overrides) rather than ignored.
