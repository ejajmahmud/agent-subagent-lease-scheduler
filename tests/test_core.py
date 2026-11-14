"""Unit tests for agent-subagent-lease-scheduler."""
import unittest
from agent_subagent_lease_scheduler.core import SubagentScheduler

class TestSubagentScheduler(unittest.TestCase):
    def setUp(self):
        self.sched = SubagentScheduler(global_token_pool=10000, max_concurrent=2)

    def test_lease_grant_and_concurrency_limit(self):
        l1 = self.sched.acquire_lease("sub1", 2000)
        l2 = self.sched.acquire_lease("sub2", 2000)
        l3 = self.sched.acquire_lease("sub3", 2000)
        self.assertIsNotNone(l1)
        self.assertIsNotNone(l2)
        self.assertIsNone(l3)

    def test_quota_exhaustion(self):
        l1 = self.sched.acquire_lease("sub_huge", 9000)
        self.assertIsNotNone(l1)
        l2 = self.sched.acquire_lease("sub_fail", 2000)
        self.assertIsNone(l2)

    def test_release_and_reclaim(self):
        l1 = self.sched.acquire_lease("sub1", 5000)
        self.sched.release_lease(l1.lease_id)
        self.assertFalse(l1.active)
        # Should be able to re-allocate
        l2 = self.sched.acquire_lease("sub2", 5000)
        self.assertIsNotNone(l2)
