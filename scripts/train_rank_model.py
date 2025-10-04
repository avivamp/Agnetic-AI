# scripts/train_rank_model.py
import os
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_rank_model")

# Try LightGBM. If not available in your local Python, create a venv with 3.10/3.11.
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder

IN_CSV = os.getenv("TRAINING_CSV", "data/search_training_latest.csv")
OUT_MODEL = os.getenv("OUT_MODEL", "models/ltr_model.txt")

os.makedirs(os.path.dirname(OUT_MODEL), exist_ok=True)

def main():
    logger.info("Reading %s", IN_CSV)
    df = pd.read_csv(IN_CSV)

    # label: purchase=1, click=0.5, else 0
    df["label"] = df["purchased"].astype(int) + 0.5 * df["clicked"].astype(int)

    # Basic safety
    df["vector_similarity"] = df["vector_similarity"].fillna(0.0)
    df["score"] = df["score"].fillna(0.0)

    # if missing hours_to_departure, set 0
    df["hours_to_departure"] = df["hours_to_departure"].fillna(0).astype(int)

    # encode cabin / loyalty
    for col in ["cabin", "loyalty_tier"]:
        df[col] = df[col].fillna("unknown")

    df["cabin_encoded"] = LabelEncoder().fit_transform(df["cabin"])
    df["loyalty_encoded"] = LabelEncoder().fit_transform(df["loyalty_tier"])

    # optional price from your catalog join; if not present, set 0
    if "price" not in df.columns:
        df["price"] = 0.0
    df["price"] = df["price"].fillna(0.0)

    # features
    features = [
        "vector_similarity",     # or "score" if that’s your pinecone score
        "price",
        "hours_to_departure",
        "cabin_encoded",
        "loyalty_encoded",
    ]

    # group by query for LambdaRank
    # each query forms a group; if you have (query, merchant_id) segments, use both
    group_sizes = df.groupby("query").size().to_numpy()

    train = lgb.Dataset(df[features], label=df["label"], group=group_sizes)

    params = dict(
        objective="lambdarank",
        metric="ndcg",
        learning_rate=0.05,
        num_leaves=31,
        feature_pre_filter=False,
    )

    logger.info("Training LightGBM LambdaRank on %d rows, %d groups", len(df), len(group_sizes))
    model = lgb.train(params, train, num_boost_round=400)

    model.save_model(OUT_MODEL)
    logger.info("Saved model to %s", OUT_MODEL)

if __name__ == "__main__":
    main()
