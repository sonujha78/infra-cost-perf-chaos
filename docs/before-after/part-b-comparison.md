# Part B — HPA Tuning: Untuned vs Tuned Comparison

## Configuration Change
| Setting | Untuned | Tuned |
|---------|---------|-------|
| scaleUp.stabilizationWindowSeconds | 0 | 30 |
| scaleDown.stabilizationWindowSeconds | 0 | 120 |
| scaleUp policy | 100% per 15s | 50% per 30s |
| scaleDown policy | 100% per 15s | 25% per 60s |

Same bursty load pattern used for both tests: 30s burst / 20s quiet, repeating.

## Untuned Result (5-min sample)
Replica count: `2→4→6→2→4→6→4→2→4→5→2→4→6→2→4→6→3→2→4→6→2→4→6...`
- Oscillated between 2 and 6 replicas roughly every 30-40 seconds
- Every burst → immediate scale-up; every quiet period → immediate scale-down
- Full log: `hpa-untuned-flapping-log.csv`

## Tuned Result (5-min sample)
Replica count: `4→4→4→4→4→6→6→6→6→6→6→6...` (stable at 6 for remainder of sample)
- Scaled up once (4→6) around the 2-minute mark, then held steady
- RPS metric itself fluctuated just as much as in the untuned run
  (ranged from ~456m to ~8184m across the sample) — the difference is
  entirely due to the stabilization window absorbing that noise instead
  of translating every fluctuation into a pod-count change
- Full log: `hpa-tuned-log.csv`

## Conclusion
The stabilization windows eliminated flapping without needing any change
to the underlying metric or threshold — the raw signal was equally noisy
in both runs. This demonstrates the core lesson from the task: reacting
to every metric fluctuation causes churn; a stabilization window makes
the autoscaler follow the *trend* instead of the *instant* value, which
is what production systems actually need under bursty, non-uniform traffic.
