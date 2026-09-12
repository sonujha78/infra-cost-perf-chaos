# HPA Flapping vs Tuned — Grafana Evidence

Screenshot: `hpa-flapping-vs-tuned-grafana.png`

Query: `kube_deployment_status_replicas{deployment="metrics-app"}` over Last 1 hour.

Timeline read left to right:
- **~08:50–09:30**: flat line at 2 replicas — baseline before either load test started
- **~09:30–09:41 (untuned ScaledObject, 0s stabilization windows)**: sharp
  sawtooth oscillation between 2 and 6 replicas, tracking every burst/quiet
  cycle of the bursty load generator almost exactly — this is the flapping
  the task calls out as a real production problem
- **~09:41 onward (tuned ScaledObject, 30s scale-up / 120s scale-down
  stabilization)**: one clean step from 4 to 6 replicas, then completely
  flat — no oscillation, despite the underlying RPS metric being just as
  noisy in this window as in the untuned one (see part-b-comparison.md)
