# KEDA (Kubernetes Event-Driven Autoscaling)

Used to drive HPA scaling from custom Prometheus metrics (requests-per-second)
instead of just CPU — because CPU-based scaling alone reacts too late or too
aggressively for bursty traffic.

Installed via:
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
kubectl create namespace keda
helm install keda kedacore/keda --namespace keda
