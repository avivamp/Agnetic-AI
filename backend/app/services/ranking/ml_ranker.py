# backend/app/services/ranking/ml_ranker.py
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

import numpy as np

logger = logging.getLogger("app.services.agentic_service")

# We try LightGBM first; if unavailable on your runtime (e.g., Python 3.13),
# fall back to a no-op ranker that simply returns the original order.
try:
    import lightgbm as lgb  # type: ignore
    _LGB_OK = True
except Exception as e:
    logger.warning("[MLRanker] LightGBM not available (%s). ML re-ranking disabled.", e)
    _LGB_OK = False


def _encode_cabin(cabin: Optional[str]) -> int:
    if not cabin:
        return 0
    cabin = cabin.lower()
    # simple ordinal encoding
    order = {"economy": 0, "premium economy": 1, "business": 2, "first": 3}
    return order.get(cabin, 0)


def _encode_loyalty(tier: Optional[str]) -> int:
    if not tier:
        return 0
    tier = tier.lower()
    order = {"blue": 0, "silver": 1, "gold": 2, "platinum": 3}
    return order.get(tier, 0)


def _hours_to_departure(iso_dt: Optional[str]) -> int:
    if not iso_dt:
        return 0
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return int(max(0, (dt - now).total_seconds() // 3600))
    except Exception:
        return 0


class MLRanker:
    """
    Loads a LightGBM LambdaRank model if present. If not present or library
    missing, acts as a pass-through (no re-ranking).
    """
    def __init__(self, model_path: Optional[str] = None):
        self.enabled = False
        self.model = None

        model_path = model_path or os.getenv("LTR_MODEL_PATH", "models/ltr_model.txt")

        if not _LGB_OK:
            return

        if os.path.isfile(model_path):
            try:
                self.model = lgb.Booster(model_file=model_path)
                self.enabled = True
                logger.info("[MLRanker] Loaded LTR model from %s", model_path)
            except Exception as e:
                logger.error("[MLRanker] Failed to load model: %s", e)
        else:
            logger.info("[MLRanker] Model file not found at %s. Re-ranking disabled.", model_path)

    def _build_feature_matrix(
        self,
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> np.ndarray:
        # Minimal, robust features you already have:
        hrs = _hours_to_departure(context.get("trip", {}).get("departure"))
        cabin_enc = _encode_cabin(context.get("cabin"))
        loyalty_enc = _encode_loyalty(context.get("loyalty_tier"))

        feats = []
        for r in results:
            # we expect Pinecone score under r["score"] and store vector_similarity = r["score"]
            vec_sim = float(r.get("score") or 0.0)
            price = float(r.get("metadata", {}).get("price") or 0.0)
            # Add more features later as needed
            feats.append([
                vec_sim,
                price,
                hrs,
                cabin_enc,
                loyalty_enc,
            ])
        return np.array(feats, dtype=float)

    def rerank(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.enabled or not results:
            return results

        try:
            X = self._build_feature_matrix(results, context)
            # LightGBM Booster.predict returns per-item scores
            scores = self.model.predict(X)
            for i, s in enumerate(scores):
                results[i]["ml_score"] = float(s)
            return sorted(results, key=lambda x: x.get("ml_score", 0.0), reverse=True)
        except Exception as e:
            logger.error("[MLRanker] Prediction failed, returning original order: %s", e)
            return results


# global instance (safe to import)
ml_ranker = MLRanker()
