# cgroups v2 — Manual Memory Limiting & OOM-Kill

## Setup
    sudo mkdir -p /sys/fs/cgroup/manual-demo
    echo "50M" | sudo tee /sys/fs/cgroup/manual-demo/memory.max
    echo "20000 100000" | sudo tee /sys/fs/cgroup/manual-demo/cpu.max   # 20% of 1 core

## Attempt 1 — FAILED, but a real and useful finding
First attempt: started a memory-hog script in the background with `&`,
then moved its PID into `manual-demo/cgroup.procs` afterward. Result:
the process allocated a full 200MB without being killed, and
`memory.events` showed `oom_kill 0`.

Root cause: two independent issues stacked:
1. **Swap.** `memory.max` only limits resident memory. With the host's
   swap enabled, the kernel could swap anonymous pages out under
   pressure instead of OOM-killing the process, so resident usage never
   actually exceeded 50M even though 200M was allocated in total.
2. **Race condition / cgroup inheritance.** In cgroup v2, moving a PID
   into a cgroup does NOT retroactively move its already-forked children.
   The bash wrapper forked a `python3` subprocess almost immediately;
   depending on scheduling, that child could start in the *parent*
   cgroup (no limit) before the PID-move command (which goes through
   `sudo`, adding latency) completed.

## Fix
1. `echo 0 | sudo tee /sys/fs/cgroup/manual-demo/memory.swap.max` —
   disable swap for this cgroup so memory pressure can't be deferred
   onto swap.
2. Made the memory-hog script join the cgroup **itself**, as its very
   first action (`echo $$ | sudo tee .../cgroup.procs`), before spawning
   the Python allocator — guaranteeing the child process inherits
   cgroup membership correctly.

## Result (correct run)
    Allocated 10MB total
    Allocated 20MB total
    Allocated 30MB total
    Allocated 40MB total
    Killed
    Exit status: 137            # 128 + SIGKILL(9)

memory.events after the kill:
    max      37    # memory.max limit was hit 37 times before the kill
    oom      1
    oom_kill 1

## Why this matters for Kubernetes
This is exactly the mechanism behind a pod showing `OOMKilled` status:
kubelet sets `memory.max` on the pod's cgroup to match
`resources.limits.memory`; when the container's resident memory hits
that ceiling, the kernel OOM-killer terminates it with SIGKILL (exit
137), the same as demonstrated here manually.

It also explains a real production gotcha: on a node with swap enabled,
a container near its memory limit may swap instead of getting OOM-killed
immediately — which is exactly why `vm.swappiness=0` (or low) is
recommended for latency-sensitive workloads (see `../sysctl/README.md`):
swapping under memory pressure causes severe, hard-to-diagnose latency
spikes long before an actual OOM-kill would have happened.
