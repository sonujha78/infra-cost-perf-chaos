# Part A — Cost Savings Estimate

## Methodology
Kubernetes schedules based on *requested* CPU/memory, not actual usage.
Freed-up requests translate directly into freed-up node capacity, which
translates into fewer/smaller nodes needed to run the same workload.
This estimate converts the freed CPU/memory requests into an equivalent
cost using AWS EC2 on-demand pricing as a reference (approximate —
actual savings depend on instance family, region, and whether the
freed capacity lets you remove whole nodes vs. just adds headroom).

Reference pricing (AWS EC2, us-east-1, on-demand, general purpose m6i family):
- m6i.xlarge: 4 vCPU / 16 GiB — ~$0.192/hr (~$140/month)
- Effective per-unit rate used below: ~$0.048/vCPU-hr, ~$0.012/GiB-hr

## Freed Capacity (from Part A right-sizing, 4 replicas of demo-app)
| Resource | Freed (cluster-wide) |
|----------|------------------------|
| CPU      | 7.8 cores (7800m)     |
| Memory   | ~2.83 GiB (2896Mi)    |

## Monthly Cost Equivalent of Freed Capacity
| Resource | Freed | Rate | Monthly Cost Equivalent |
|----------|-------|------|---------------------------|
| CPU      | 7.8 cores  | $0.048/vCPU-hr × 730 hr | ~$273/month |
| Memory   | 2.83 GiB   | $0.012/GiB-hr × 730 hr  | ~$25/month  |
| **Total**|            |                         | **~$298/month freed, per 4-replica app** |

## Scaling Consideration
This is for a *single* 4-replica demo app. In a real cluster running
dozens of similarly over-provisioned deployments (a common real-world
pattern — teams set requests defensively and never revisit them), this
freed capacity compounds:
- It can allow the cluster autoscaler to **remove whole nodes** that are
  no longer needed once pods pack more efficiently, rather than just
  freeing fragmented headroom on existing nodes
- 10 similar deployments at this ratio → ~$3,000/month in freed capacity
  or removable node cost

## Caveat
This is an approximate, directional estimate — not a guaranteed billing
reduction. Actual savings materialize only if:
1. The cluster autoscaler (or manual node management) actually scales
   down nodes when aggregate requests drop, and
2. The freed capacity isn't immediately consumed by other over-provisioned
   workloads scheduling into the same slack

Real dollar savings should be confirmed against actual cloud billing
before/after a rollout, ideally via the cloud provider's own cost
explorer/calculator for the exact instance types in use.
