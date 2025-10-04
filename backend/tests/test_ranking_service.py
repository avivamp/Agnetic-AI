import pytest
from datetime import datetime, timedelta, timezone
from app.services.ranking_service import rank_products, compute_merchant_boost, ml_infer_score

# --- MOCK DATA SETUP --------------------------------------------------------

MOCK_MATCHES = [
    {
        "id": "p1",
        "score": 0.85,
        "metadata": {"category": "Perfume", "price": 120, "name": "Luxury Lavender"},
    },
    {
        "id": "p2",
        "score": 0.65,
        "metadata": {"category": "Perfume", "price": 70, "name": "Mid Range Perfume"},
    },
    {
        "id": "p3",
        "score": 0.45,
        "metadata": {"category": "Baby & Kids", "price": 25, "name": "Baby Lotion"},
    },
]

MERCHANT_ID = "airlinex"

FULL_CONTEXT = {
    "trip": {
        "from": "DXB",
        "to": "CDG",
        "departure": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
    },
    "cabin": "Business",
    "loyalty_tier": "Gold",
    "user_id_hash": "sha256:abcd1234"
}

# --- TEST CASES -------------------------------------------------------------

def test_rank_products_with_full_context(monkeypatch):
    """Ensure full context produces sorted scores and consistent ranking."""
    ranked = rank_products(MOCK_MATCHES, MERCHANT_ID, FULL_CONTEXT)

    assert isinstance(ranked, list)
    assert "rank_score" in ranked[0]
    assert ranked[0]["rank_score"] >= ranked[-1]["rank_score"]
    assert all(0.0 <= item["rank_score"] <= 1.0 for item in ranked)


def test_rank_products_with_minimal_context():
    """Should not fail when context is missing."""
    ranked = rank_products(MOCK_MATCHES, MERCHANT_ID)
    assert len(ranked) == len(MOCK_MATCHES)
    assert all("rank_score" in item for item in ranked)


def test_ml_infer_score_business_gold():
    """ML score should increase with business + gold combo."""
    score = ml_infer_score(
        {"metadata": {"category": "Perfume"}}, FULL_CONTEXT
    )
    assert 0.7 <= score <= 1.0


def test_compute_merchant_boost_safety():
    """compute_merchant_boost should never crash on missing data."""
    boost = compute_merchant_boost("unknown_merchant", "Perfume", None, None)
    assert isinstance(boost, (int, float))
    assert boost >= 0.0


def test_ranking_blending(monkeypatch):
    """If vector similarity changes, ranking should reflect it."""
    matches_high_vec = [
        {"metadata": {"category": "Perfume"}, "score": 0.9},
        {"metadata": {"category": "Perfume"}, "score": 0.1},
    ]
    ranked = rank_products(matches_high_vec, MERCHANT_ID, FULL_CONTEXT)
    assert ranked[0]["score"] >= ranked[1]["score"]


def test_trip_time_boost():
    """ML score should be higher for near departure."""
    ctx_soon = {
        "trip": {"departure": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()},
        "cabin": "Economy",
        "loyalty_tier": "Silver"
    }
    ctx_far = {
        "trip": {"departure": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()},
        "cabin": "Economy",
        "loyalty_tier": "Silver"
    }

    s_soon = ml_infer_score({}, ctx_soon)
    s_far = ml_infer_score({}, ctx_far)
    assert s_soon >= s_far


def test_rank_order_consistency():
    """Top-ranked product should have the highest final score."""
    ranked = rank_products(MOCK_MATCHES, MERCHANT_ID, FULL_CONTEXT)
    scores = [r["rank_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)
