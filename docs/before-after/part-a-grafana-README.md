# Part A — Grafana Evidence: Usage vs Requests

Screenshots: `part-a-grafana-usage-vs-requests.png`, `part-a-grafana-requests-flat.png`

Queries used (Explore, Prometheus datasource, Last 6 hours):
- Actual usage: `sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"demo-app-.*"}[2m])) by (pod) * 1000`
- Requested: `sum(kube_pod_container_resource_requests{namespace="default", pod=~"demo-app-.*", resource="cpu"}) by (pod) * 1000`

## Important honest caveat
This graph's visible window only covers the period **after** right-sizing
was applied — the `requested` line is flat at 50m for the entire window.
The original 2000m-request "before" state is not visible here because:
Prometheus was configured with `retention=6h` (see
`../../monitoring/prometheus/README.md`), and by the time this graph was
captured, enough real time had passed that the original over-provisioned
period had already rolled off Prometheus's retention window.

## What this graph does show
- demo-app pods: actual CPU usage steady around 4-6m against a 50m
  request — confirms the right-sized value (set from the VPA
  recommendation of 25m target + headroom) remains appropriately sized
  in steady state, neither over- nor under-provisioned.
- metrics-app pods: visible usage spikes up to ~10m during the bursty
  load test windows (Part B), dropping back to baseline afterward —
  visually correlates with the load generator's on/off cycle.

## Where the actual before/after CPU numbers live
The real before (2000m request / ~1m actual usage) vs after (50m
request / ~3m actual usage) comparison — captured via `kubectl top`
at the time of the change, before Prometheus's retention window would
have rolled it off — is documented with exact numbers in
`part-a-before.md` and `part-a-after.md` in this same directory.
