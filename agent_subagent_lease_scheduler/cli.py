"""CLI for agent-subagent-lease-scheduler."""
import argparse
import sys
from .core import SubagentScheduler

def main():
    parser = argparse.ArgumentParser(description="Agent Subagent Lease Scheduler CLI")
    parser.add_argument("--demo", action="store_true", help="Run subagent lease scheduler demo")
    args = parser.parse_args()

    if args.demo:
        sched = SubagentScheduler(global_token_pool=20000, max_concurrent=2)
        l1 = sched.acquire_lease("crawler_1", 8000, ttl_seconds=10.0)
        l2 = sched.acquire_lease("indexer_2", 8000, ttl_seconds=10.0)
        l3 = sched.acquire_lease("analyzer_3", 8000, ttl_seconds=10.0)  # Should fail due to max_concurrent

        print(f"[+] Lease 1 granted: {l1.lease_id if l1 else 'DENIED'}")
        print(f"[+] Lease 2 granted: {l2.lease_id if l2 else 'DENIED'}")
        print(f"[+] Lease 3 granted: {l3.lease_id if l3 else 'DENIED (Rate/Concurrency Protected)'}")

        sched.release_lease(l1.lease_id)
        print(f"[+] Released {l1.lease_id}. Trying Lease 3 again...")
        l3_retry = sched.acquire_lease("analyzer_3", 8000)
        print(f"[+] Lease 3 retry granted: {l3_retry.lease_id if l3_retry else 'DENIED'}")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
