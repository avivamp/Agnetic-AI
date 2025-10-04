# backend/app/config/merchant_weights.py

"""
Merchant-specific configuration for ranking and personalization weights.
These can later be made editable via the Merchant Admin Dashboard UI.
"""

MERCHANT_RULES = {
    "airlinex": {
        # === Base blend weights ===
        # Controls how much each signal contributes to the final score.
        # These can be tuned per merchant via dashboard sliders.
        "blend_weights": {
            "ml": 0.6,            # weight of ML-predicted engagement score
            "boost": 0.3,         # weight of merchant-specific category boosts
            "similarity": 0.1     # weight of vector similarity relevance
        },

        # === Category Boosts ===
        # Used to promote specific categories (e.g., seasonal focus).
        "category_boosts": {
            "Fragrance & Beauty": 1.2,
            "Electronics": 1.1,
            "Baby & Kids": 1.05,
            "Luxury": 1.3,
            "Comfort": 1.0,
        },

        # === Trip-based rules ===
        # Can promote products depending on route or destination.
        "trip_rules": [
            {
                "route": ["DXB", "CDG"],       # if flying to Paris
                "boost_category": "Fragrance & Beauty",
                "weight": 1.25,                # prioritize perfumes
            },
            {
                "route": ["DXB", "LHR"],       # if flying to London
                "boost_category": "Luxury",
                "weight": 1.3,
            }
        ],

        # === Cabin class specific boosts ===
        "cabin_rules": {
            "business": {
                "luxury_category_boost": 1.2,  # push luxury or high-end items
                "comfort_category_boost": 1.1
            },
            "first": {
                "luxury_category_boost": 1.4,
                "comfort_category_boost": 1.2
            },
            "economy": {
                "comfort_category_boost": 1.0
            }
        },

        # === Loyalty Tier Adjustments ===
        # Gold & Platinum flyers see more premium options first.
        "loyalty_weights": {
            "silver": 1.0,
            "gold": 1.1,
            "platinum": 1.2
        },
    },

    # Example second merchant (expand as you onboard more)
    "dnata_shop": {
        "blend_weights": {
            "ml": 0.5,
            "boost": 0.4,
            "similarity": 0.1
        },
        "category_boosts": {
            "Travel Essentials": 1.2,
            "Gadgets": 1.1
        },
        "cabin_rules": {
            "business": {"luxury_category_boost": 1.15},
            "economy": {"comfort_category_boost": 1.0}
        },
        "trip_rules": [],
        "loyalty_weights": {"silver": 1.0, "gold": 1.05, "platinum": 1.1},
    },
}
