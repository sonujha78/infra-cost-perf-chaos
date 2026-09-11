# Metrics Server

Installed via upstream manifest, patched for kind's self-signed kubelet certs:

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

Why `--kubelet-insecure-tls`: kind nodes use self-signed kubelet serving certs not
signed by a CA metrics-server trusts by default. In a real cloud cluster this flag
would NOT be used — kubelet certs would be properly signed instead.
