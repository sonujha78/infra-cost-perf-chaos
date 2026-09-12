# ulimits — Diagnosing & Fixing EMFILE at the systemd Unit Level

## The problem
A common production failure: a service (API server, database connection
pool, etc.) hits "Too many open files" (EMFILE, errno 24) under load
because its file-descriptor limit is lower than what it actually needs.

Critically: `ulimit -n <value>` set in an interactive shell only affects
that shell session and anything forked directly from it. It does **not**
persist across reboots, and it has **no effect** on services started by
systemd (which don't inherit a login shell's ulimits) — this is why
"just raise ulimit -n" is the wrong fix for a systemd-managed service.

## Reproducing the failure
A oneshot systemd service (`file-opener-demo.service`) runs a Python
script that opens files in a loop until it hits its file-descriptor
limit, deliberately constrained with a low `LimitNOFILE`:

    [Service]
    Type=oneshot
    ExecStart=/usr/bin/python3 /tmp/file-opener.py
    LimitNOFILE=256

Result:
    Soft limit: 256, Hard limit: 256
    FAILED after opening 253 files: [Errno 24] Too many open files

253/256 files opened before hitting the ceiling (the remaining few fds
are consumed by stdin/stdout/stderr and Python's own internals).

## The fix — systemd unit level, not shell ulimit
    [Service]
    Type=oneshot
    ExecStart=/usr/bin/python3 /tmp/file-opener.py
    LimitNOFILE=100000

Result:
    Soft limit: 100000, Hard limit: 100000
    FAILED after opening 99997 files: [Errno 24] Too many open files

## Before / After
| Config | Files opened before EMFILE |
|--------|------------------------------|
| LimitNOFILE=256 (unfixed) | 253 |
| LimitNOFILE=100000 (fixed) | 99997 |

## Why this is the correct, persistent fix
- `LimitNOFILE=` in a systemd unit file is applied by systemd itself
  when it forks the service process — it survives reboots, service
  restarts, and doesn't depend on which shell (if any) started the
  service.
- This is exactly how Kubernetes and container runtimes handle the same
  problem for containerized workloads (setting rlimits at container
  creation via the container runtime spec) — the systemd-unit case here
  is the same mechanism one layer down, for services running directly
  on the host.
