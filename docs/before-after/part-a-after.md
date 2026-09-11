# Part A — Resource Right-Sizing: AFTER State

## Methodology
1. Deployed demo-app with deliberately inflated requests (2 CPU / 1Gi memory)
2. Installed metrics-server to capture real usage via `kubectl top`
3. Ran a continuous load generator (busybox wget loop, ~20 concurrent
   requests per batch) against the app for several minutes
4. Installed VPA in recommendation mode (`updateMode: "Off"`) targeting
   the demo-app deployment
5. Let VPA observe usage over time and produce a recommendation
6. Manually right-sized requests/limits based on the VPA recommendation
   plus a safety headroom margin (VPA gives a target, not a hard rule —
   headroom protects against traffic spikes VPA hasn't seen yet)

## VPA Recommendation (from `kubectl describe vpa demo-app-vpa`)
| Metric | Lower Bound | Target | Upper Bound |
|--------|-------------|--------|-------------|
| CPU    | 25m         | 25m    | 2000m       |
| Memory | 250Mi       | 250Mi  | 1Gi         |

## Right-Sizing Decision (per pod)
| Resource | Before (request) | VPA Target | After (request) | Headroom applied |
|----------|-------------------|------------|-------------------|-------------------|
| CPU      | 2000m             | 25m        | **50m**            | 2x over target |
| Memory   | 1024Mi (1Gi)      | 250Mi      | **300Mi**          | +20% over target |

Limits set to 200m CPU / 400Mi memory (4x / 1.33x of requests) to allow
burst headroom without letting a single pod monopolize a node.

## Cluster-Wide Impact (4 replicas)
| Resource | Before (total requested) | After (total requested) | Freed up |
|----------|---------------------------|---------------------------|----------|
| CPU      | 8000m (8 cores)           | 200m (0.2 cores)          | **7800m (7.8 cores) — 97.5% reduction** |
| Memory   | 4096Mi (4Gi)              | 1200Mi (~1.17Gi)          | **2896Mi (~2.83Gi) — 70.7% reduction** |

## Why this matters
Kubernetes schedules pods based on *requests*, not actual usage. Before
right-sizing, these 4 pods were reserving 8 full CPU cores and 4Gi of
memory on the cluster — capacity that other pods could not schedule into,
even though actual usage was under 1% of that reservation. After
right-sizing, the same workload reserves only 0.2 cores and ~1.17Gi,
freeing 7.8 cores and ~2.83Gi of schedulable capacity cluster-wide for
other workloads — capacity that would otherwise sit idle and unusable.

See `../cost-report/part-a-cost-savings.md` for the dollar-cost translation
of this freed capacity.
