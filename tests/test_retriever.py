"""
test_retriever.py — unit tests for the retrieval component (the part
that works fully offline and deterministically, unlike LLM generation).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from retriever import Retriever

def test_retriever_loads():
    r = Retriever()
    assert len(r.documents) > 0

def test_tenant_query_returns_tenant_docs():
    r = Retriever()
    results = r.retrieve("landlord eviction notice", top_k=2)
    assert len(results) > 0
    assert all(res["source"] == "tenant_rights.txt" for res in results)

def test_employment_query_returns_employment_docs():
    r = Retriever()
    results = r.retrieve("maternity leave weeks entitled", top_k=2)
    assert len(results) > 0
    assert results[0]["source"] == "employment_rights.txt"

def test_consumer_query_returns_consumer_docs():
    r = Retriever()
    results = r.retrieve("consumer complaint district commission", top_k=2)
    assert len(results) > 0
    assert results[0]["source"] == "consumer_rights.txt"

def test_irrelevant_query_returns_low_or_no_results():
    r = Retriever()
    results = r.retrieve("how to bake a chocolate cake", top_k=3, min_score=0.15)
    assert len(results) == 0

def test_results_are_score_sorted():
    r = Retriever()
    results = r.retrieve("security deposit rental agreement", top_k=5)
    scores = [res["score"] for res in results]
    assert scores == sorted(scores, reverse=True)

if __name__ == "__main__":
    tests = [test_retriever_loads, test_tenant_query_returns_tenant_docs,
             test_employment_query_returns_employment_docs, test_consumer_query_returns_consumer_docs,
             test_irrelevant_query_returns_low_or_no_results, test_results_are_score_sorted]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
