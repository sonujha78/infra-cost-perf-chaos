# CPU Noisy-Neighbor Test — Kubernetes-level attempt (kind cluster)

## Goal
Show that a noisy neighbor pod without CPU limits can starve a critical pod
on the same node, then show that cgroup limits prevent this.

## Setup
- critical-app: Deployment, 1 replica, originally with limits.cpu=500m,
  later patched to remove limits to simulate an unprotected workload
- noisy-neighbor: plain Pod (vish/stress image, idle) + Chaos Mesh
  StressChaos injecting CPU load (workers=16, load=100)

## Attempts and findings
1. First attempts used `-cpus N` args directly on stress pods and Chaos Mesh
   StressChaos, but the underlying kind node (`cost-perf-chaos-worker2`) runs
   as a Docker container on a 12-core host, so demand never reliably exceeded
   available capacity — no real contention appeared.
2. Constrained the kind node's real capacity via
   `docker update --cpus="2" cost-perf-chaos-worker2` to force a small,
   guaranteed-scarce CPU pool. `kubectl top node` confirmed the cap took
   effect (usage capped at ~2001m).
3. Even with the 2-core cap, `kubectl top pods` numbers for critical-app and
   noisy-neighbor did not consistently sum to the node total, and critical-app's
   reported usage did not show clear starvation. This points to metrics-server
   reporting being unreliable in this nested kind-in-Docker environment
   (extra cgroup layers between the container runtime and the host).

## Conclusion
Kubernetes-level (kubectl top) observation is not reliable enough in this
nested kind setup to cleanly demonstrate noisy-neighbor starvation. Moving
to direct host-level cgroups v2 (outside Kubernetes) for this experiment,
which is also what Part C of the task explicitly calls for ("cgroup limits
for a process outside Kubernetes").
