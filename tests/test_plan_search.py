from backend.plan_search import PlanSearchIndex, embed

SAMPLE_PLANS = [
    {"id": 1, "name": "Basic Lite", "monthly_price": 249, "data_gb": 10, "description": "cheapest plan minimal data light users"},
    {"id": 2, "name": "Business Pro", "monthly_price": 1499, "data_gb": 500, "description": "priority network international roaming"},
]


def test_embed_returns_normalized_vector():
    vec = embed("cheap plan")
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-5 or norm == 0.0  # normalized, or all-zero for empty input


def test_embed_empty_string_returns_zero_vector():
    vec = embed("")
    assert all(x == 0.0 for x in vec)


def test_search_returns_empty_list_before_build():
    index = PlanSearchIndex()
    assert index.search("anything") == []


def test_search_finds_relevant_plan_by_id():
    index = PlanSearchIndex()
    index.build(SAMPLE_PLANS)
    results = index.search("cheapest plan with minimal data", k=1)
    assert results == [1]


def test_search_respects_k():
    index = PlanSearchIndex()
    index.build(SAMPLE_PLANS)
    results = index.search("any plan", k=1)
    assert len(results) == 1


def test_rebuild_replaces_previous_index():
    index = PlanSearchIndex()
    index.build(SAMPLE_PLANS)
    index.build(SAMPLE_PLANS[:1])
    assert index.index.ntotal == 1
