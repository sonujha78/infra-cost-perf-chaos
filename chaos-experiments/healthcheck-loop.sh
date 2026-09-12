#!/bin/bash
# Continuous health check against demo-app, logs success/failure with timestamp
SUCCESS=0
FAIL=0
for i in $(seq 1 300); do
  if kubectl run healthcheck-tmp-$i --image=busybox:1.36 --rm -i --restart=Never --quiet -- \
     wget -q -O- -T 2 http://demo-app.default.svc.cluster.local/ > /dev/null 2>&1; then
    SUCCESS=$((SUCCESS+1))
    echo "$(date +%T) OK"
  else
    FAIL=$((FAIL+1))
    echo "$(date +%T) FAIL"
  fi
  sleep 1
done
echo "TOTAL: success=$SUCCESS fail=$FAIL"
