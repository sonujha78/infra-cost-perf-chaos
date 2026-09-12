# Network Chaos — Latency + Packet Loss

## Setup
- Client: a pod calling `metrics-app` once per second, with retry logic
  (up to 3 attempts, 2s timeout each, 0.5s between retries) — simulating
  a real service client rather than a bare healthcheck.
- Injected via Chaos Mesh, targeting `metrics-app` pods, for a 40s window:
  - `NetworkChaos` action=delay: 500ms latency, 100ms jitter
  - `NetworkChaos` action=loss: 25% packet loss
  (both applied concurrently to the same target)

## Result
    TOTAL: success=90 fail=0 (of which recovered-via-retry=1)

- 90/90 requests eventually succeeded — zero requests were lost outright.
- During the chaos window, request cadence visibly slowed (gaps of 2-4s
  between requests instead of the normal 1s), directly reflecting the
  injected latency.
- One request hit a full `wget: download timed out` and required a retry
  to succeed — direct evidence the retry logic is doing real work, not
  just padding, under 25% packet loss + 500ms±100ms latency.
- After the chaos window ended (~08:43:00), request cadence returned to
  a clean 1s interval with no further retries.

## Conclusion
The client's timeout+retry logic successfully absorbed both latency and
packet loss injected directly at the network layer between two services —
degraded performance (slower requests, one retry) instead of cascading
into request failures or a full outage. This validates that basic
client-side resilience (bounded retries with a timeout) is enough to
survive realistic transient network degradation between services, which
is exactly the pattern a service mesh's retry policies or a well-written
HTTP client automate in production.
