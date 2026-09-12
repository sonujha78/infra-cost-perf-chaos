# Part B — HPA Autoscaling: UNTUNED Behavior (Flapping)

## Configuration
- KEDA ScaledObject targeting `metrics-app` deployment
- Trigger: Prometheus query `sum(rate(nginx_http_requests_total[30s]))`, threshold 5 RPS/replica
- minReplicas: 2, maxReplicas: 10
- **scaleUp.stabilizationWindowSeconds: 0** (react instantly)
- **scaleDown.stabilizationWindowSeconds: 0** (react instantly)

## Load Pattern
Bursty traffic: 30s high load (~30 concurrent requests looped) / 20s quiet, repeating continuously.

## Observed Result (5-minute sample, replicas polled every 5s)
See `hpa-untuned-flapping-log.csv` for the full log. Replica count over
the sample period:

2 → 4 → 6 → 2 → 4 → 6 → 4 → 2 → 4 → 5 → 2 → 4 → 6 → 2 → 4 → 6 → 3 → 2 →
4 → 6 → 2 → 4 → 6 → ...

Replicas oscillated between 2 and 6 roughly every 30-40 seconds, tracking
each burst/quiet cycle almost exactly — confirming the HPA has **zero
damping**: every burst triggers an immediate scale-up, every quiet period
triggers an immediate scale-down, with no memory of recent history.

## Why this is a problem in production
- Constant pod churn wastes scheduling overhead, image-already-cached
  benefits are lost on churn, and new pods need warm-up time (JIT
  compilation, connection pool warm-up, cache misses) right when they're
  needed most
- If a burst is followed by a brief lull, the system scales down just
  before the next burst arrives — causing latency spikes while new pods
  spin up again
- This is the "real, common production problem" the task calls out:
  CPU-alone or naive threshold-based scaling without stabilization
  windows causes exactly this kind of oscillation under bursty traffic
