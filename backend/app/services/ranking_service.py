import logging
from typing import List, Dict, Any
from app.config.merchant_weights import MERCHANT_RULES

logger = logging.getLogger("app.services.ranking_service")


def compute_merchant_boost(merchant_id, category, trip=None, cabin=None):
    merchant = MERCHANT_RULES.get(merchant_id, {})
    boost = merchant.get("category_boosts", {}).get(category, 1.0)

    # Trip-specific boost
    if trip:
        for rule in merchant.get("trip_rules", []):
            if trip.get("from") in rule.get("route", []) and trip.get("to") in rule.get("route", []):
                if rule.get("boost_category") == category:
                    boost *= rule.get("weight", 1.0)

    # Cabin-based adjustment
    if cabin:
        cabin_rules = merchant.get("cabin_rules", {}).get(cabin.lower(), {})
        boost *= cabin_rules.get("luxury_category_boost", 1.0)

    return boost


def ml_infer_score(item: Dict[str, Any], context: Dict[str, Any]) -> float:
    """Heuristic ML-based score (placeholder for real model)."""
    base = 0.5
    if not context:
        return base

    cabin = context.get("cabin", "").lower()
    loyalty = context.get("loyalty_tier", "").lower()
    trip = context.get("trip", {})

    if "business" in cabin:
        base += 0.2
    elif "first" in cabin:
        base += 0.3
    if "gold" in loyalty:
        base += 0.1

    if trip.get("departure"):
        from datetime import datetime, timezone
        dep_time = datetime.fromisoformat(trip["departure"].replace("Z", "+00:00"))
        time_till_departure = max(0, (dep_time - datetime.now(timezone.utc)).days)
        if time_till_departure < 3:
            base += 0.05

    return min(1.0, base)


def rank_products(matches: List[Dict[str, Any]], merchant_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Blend ML model score, merchant-defined boost, and vector similarity."""
    merchant = MERCHANT_RULES.get(merchant_id, {})
    blend_weights = merchant.get("blend_weights", {"ml": 0.6, "boost": 0.3, "similarity": 0.1})

    ranked = []

    for m in matches:
        meta = m.get("metadata", {})
        category = meta.get("category", "General")
        vector_similarity = m.get("score", 0.0)

        ml_score = ml_infer_score(m, context)
        merchant_boost_weight = compute_merchant_boost(merchant_id, category, context.get("trip"), context.get("cabin"))

        final_score = (
            blend_weights["ml"] * ml_score +
            blend_weights["boost"] * merchant_boost_weight +
            blend_weights["similarity"] * vector_similarity
        )

        final_score = max(0, min(1, final_score))
        m["rank_score"] = round(final_score, 4)
        ranked.append(m)

        logger.debug(
            f"[Rank] merchant={merchant_id}, id={m.get('id')} cat={category} "
            f"ml={ml_score:.2f}, boost={merchant_boost_weight:.2f}, vec={vector_similarity:.2f}, "
            f"final={final_score:.3f}"
        )

    ranked.sort(key=lambda x: x["rank_score"], reverse=True)
    return ranked
