# Infrastructure Cost & Performance Optimization + Chaos Engineering

Production-grade DevOps project: taking a running app and making it cheaper
and more resilient via Kubernetes right-sizing, HPA tuning, kernel-level
Linux tuning (cgroups, sysctl, ulimits), and chaos engineering validation.

## Stack
Terraform · Kubernetes (HPA/VPA) · Chaos Mesh/Litmus · Linux kernel tuning
(cgroups v2, sysctl, strace/perf/bpftrace) · Prometheus/Grafana

## Structure
- `terraform/` — node pool / infra definitions
- `k8s-manifests/` — app deployment, HPA, VPA configs
- `kernel-tuning/` — cgroups, sysctl, ulimit configs + explanations
- `profiling/` — strace, perf, bpftrace outputs and findings
- `chaos-experiments/` — Litmus/Chaos Mesh experiment YAMLs + results
- `monitoring/` — Prometheus/Grafana setup and dashboards
- `docs/` — before/after graphs, cost report, findings

## Status
🚧 In progress — see commit history for phase-by-phase progress.
