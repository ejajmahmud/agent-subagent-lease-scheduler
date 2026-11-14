"""Core subagent lease scheduler implementation."""
import time
from typing import Dict, Optional, List

class TaskLease:
    def __init__(self, lease_id: str, subagent_id: str, quota_tokens: int, ttl_seconds: float = 30.0):
        self.lease_id = lease_id
        self.subagent_id = subagent_id
        self.quota_tokens = quota_tokens
        self.ttl_seconds = ttl_seconds
        self.created_at = time.time()
        self.last_heartbeat = self.created_at
        self.tokens_used = 0
        self.active = True

    @property
    def is_expired(self) -> bool:
        if not self.active:
            return True
        return (time.time() - self.last_heartbeat) > self.ttl_seconds

    def heartbeat(self, tokens_consumed: int = 0):
        self.last_heartbeat = time.time()
        self.tokens_used += tokens_consumed

class QuotaManager:
    def __init__(self, global_token_pool: int = 100000):
        self.global_token_pool = global_token_pool
        self.allocated_tokens = 0

    def can_allocate(self, amount: int) -> bool:
        return (self.allocated_tokens + amount) <= self.global_token_pool

    def allocate(self, amount: int) -> bool:
        if self.can_allocate(amount):
            self.allocated_tokens += amount
            return True
        return False

    def release(self, amount: int):
        self.allocated_tokens = max(0, self.allocated_tokens - amount)

class SubagentScheduler:
    def __init__(self, global_token_pool: int = 50000, max_concurrent: int = 5):
        self.quota_mgr = QuotaManager(global_token_pool)
        self.max_concurrent = max_concurrent
        self.leases: Dict[str, TaskLease] = {}
        self._seq = 0

    def acquire_lease(self, subagent_id: str, tokens_needed: int, ttl_seconds: float = 30.0) -> Optional[TaskLease]:
        self.reclaim_expired()
        active_count = sum(1 for l in self.leases.values() if not l.is_expired)
        if active_count >= self.max_concurrent:
            return None
        if not self.quota_mgr.allocate(tokens_needed):
            return None

        self._seq += 1
        lease_id = f"lease_{self._seq}_{subagent_id}"
        lease = TaskLease(lease_id, subagent_id, tokens_needed, ttl_seconds)
        self.leases[lease_id] = lease
        return lease

    def release_lease(self, lease_id: str):
        lease = self.leases.get(lease_id)
        if lease and lease.active:
            lease.active = False
            unused = max(0, lease.quota_tokens - lease.tokens_used)
            self.quota_mgr.release(unused)

    def reclaim_expired(self) -> int:
        reclaimed = 0
        for l in self.leases.values():
            if l.active and l.is_expired:
                l.active = False
                unused = max(0, l.quota_tokens - l.tokens_used)
                self.quota_mgr.release(unused)
                reclaimed += 1
        return reclaimed
