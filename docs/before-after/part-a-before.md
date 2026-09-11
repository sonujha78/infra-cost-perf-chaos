# Part A — Resource Right-Sizing: BEFORE State

## Deployment: demo-app (4 replicas, nginx:1.27-alpine)

### Configured Resources (per pod)
| Resource | Request | Limit |
|----------|---------|-------|
| CPU      | 2000m   | 2500m |
| Memory   | 1Gi     | 1.5Gi |

### Actual Usage (idle, captured via `kubectl top pods`, 60s after rollout)
| Pod | CPU Used | Memory Used |
|-----|----------|-------------|
| demo-app-6d67649c6b-6rmj7 | 1m | 10Mi |
| demo-app-6d67649c6b-7sc54 | 1m | 9Mi  |
| demo-app-6d67649c6b-khvl6 | 1m | 9Mi  |
| demo-app-6d67649c6b-rwfbl | 1m | 10Mi |

### Over-provisioning Ratio
- CPU: requested 2000m, using ~1m → **~0.05% utilization**
- Memory: requested 1024Mi, using ~9-10Mi → **~1% utilization**

### Cluster-Wide Waste (4 replicas)
- Total CPU requested: 8000m (8 full cores) — of which ~4m actually used
- Total memory requested: 4096Mi (4Gi) — of which ~38Mi actually used

This is the starting point before load testing and VPA-based right-sizing.
Note: this snapshot is taken at idle (no traffic yet) — a load test will be
run next to capture realistic usage under actual request volume before
final right-sizing decisions are made.
