"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    FG164 Cross Engine Cache Integration & Memoization Test.
    Validates deterministic key hashing, TTL expiration, cross-engine memoization,
    and performance statistics.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.
===============================================================================
"""

import sys
import os
import time

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from tools.eos.cache.runtime_cache import RuntimeCache
from tools.eos.cache.cache_provider import CacheProvider
from tools.eos.cache.cache_keys import CacheKeys


def test_runtime_cache():
    print("===============================================================================")
    print("WILSY OS KERNEL - FG164 CROSS ENGINE CACHE VERIFICATION")
    print("===============================================================================")

    cache = RuntimeCache()

    # 1. Test Cache Key generation
    repo_key = CacheKeys.repository_scan_key("/path/to/repo", {"branch": "main"})
    ai_key = CacheKeys.ai_inference_key("GPT-4", "Analyze architecture", {"temp": 0.2})
    quality_key = CacheKeys.quality_audit_key("mod-01", "v2.1")
    
    print(f"  -> Generated Repo Scan Cache Key: [{repo_key}]")
    print(f"  -> Generated AI Inference Key:   [{ai_key}]")
    print(f"  -> Generated Quality Audit Key:  [{quality_key}]")
    
    assert "eos:cache:repo:scan:" in repo_key
    assert "eos:cache:ai:GPT-4:" in ai_key
    assert "eos:cache:quality:mod-01:v2.1" == quality_key

    # 2. Test Set and Get operations
    cache.set(repo_key, {"files_scanned": 1500, "status": "clean"})
    cached_val = cache.get(repo_key)
    print(f"  -> Retrieved cached value: {cached_val}")
    assert cached_val is not None
    assert cached_val["files_scanned"] == 1500

    # 3. Test Memoization (get_or_compute)
    computation_counter = {"count": 0}

    def expensive_computation() -> str:
        computation_counter["count"] += 1
        return "expensive-result-data"

    # First call: cache miss, should compute
    res1 = cache.get_or_compute(ai_key, expensive_computation)
    # Second call: cache hit, should NOT compute
    res2 = cache.get_or_compute(ai_key, expensive_computation)

    print(f"  -> Memoization results: res1=[{res1}], res2=[{res2}]")
    print(f"  -> Computation execution count: [{computation_counter['count']}] (Expected: 1)")
    assert res1 == "expensive-result-data"
    assert res2 == "expensive-result-data"
    assert computation_counter["count"] == 1

    # 4. Test TTL Expiration
    short_key = CacheKeys.custom_key("test", "ttl", {"test": "val"})
    cache.set(short_key, "temporary-data", ttl_seconds=0.5)
    
    assert cache.get(short_key) == "temporary-data"
    print("  -> TTL item present immediately.")
    
    print("  -> Waiting for TTL expiration (0.6s)...")
    time.sleep(0.6)
    
    expired_val = cache.get(short_key)
    print(f"  -> Value after TTL expiration: [{expired_val}] (Expected: None)")
    assert expired_val is None

    # 5. Test Cache Statistics
    stats = cache.get_stats()
    print(f"  -> Cache Statistics:")
    print(f"     - Total Items: {stats['total_items']}")
    print(f"     - Hits: {stats['hits']}")
    print(f"     - Misses: {stats['misses']}")
    print(f"     - Hit Ratio: {stats['hit_ratio_percent']}%")
    assert stats["hits"] >= 2
    assert stats["misses"] >= 2

    print("===============================================================================")
    print("FG164 CROSS ENGINE CACHE VERIFIED SUCCESSFULLY.")
    print("===============================================================================")


if __name__ == "__main__":
    test_runtime_cache()
