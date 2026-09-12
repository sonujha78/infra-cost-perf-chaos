# Prometheus + Grafana Stack

Installed via kube-prometheus-stack Helm chart:

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install kube-prom-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=6h

Note: run without `--wait` — first-time image pulls for this stack can
exceed Helm's default wait timeout even though installation succeeds.
Poll with `kubectl get pods -n monitoring -w` instead.

## Access
Grafana:
  kubectl --namespace monitoring port-forward svc/kube-prom-stack-grafana 3000:80
  # then open http://localhost:3000  (user: admin / password: admin123)

Prometheus:
  kubectl --namespace monitoring port-forward svc/kube-prom-stack-kube-prome-prometheus 9090:9090
  # then open http://localhost:9090
