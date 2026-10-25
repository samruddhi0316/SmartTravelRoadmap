import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------------
# LOAD PLACES
# -----------------------------------

def load_places():
    """
    Load travel places from CSV.
    """
    return pd.read_csv("data/places.csv")


# -----------------------------------
# RULE-BASED SCORE
# -----------------------------------

def calculate_score(
    row,
    budget,
    preferred_duration=None
):
    """
    Calculate recommendation score using:
    1. Rating
    2. Budget suitability
    3. Duration suitability
    """

    # --------------------------------
    # 1. Rating Score
    # --------------------------------

    rating_score = row["rating"] / 5


    # --------------------------------
    # 2. Budget Score
    # --------------------------------

    if budget is None:

        budget_score = 1

    else:

        cost = row["cost"]

        if cost <= budget:

            budget_score = (
                1 - (cost / budget) * 0.3
            )

            budget_score = max(
                0,
                min(1, budget_score)
            )

        else:

            budget_score = max(
                0,
                1 - ((cost - budget) / budget)
            )


    # --------------------------------
    # 3. Duration Score
    # --------------------------------

    if preferred_duration is None:

        duration_score = 1

    else:

        difference = abs(
            row["duration"]
            - preferred_duration
        )

        duration_score = max(
            0,
            1 - (
                difference
                / preferred_duration
            )
        )


    # --------------------------------
    # FINAL SCORE
    # --------------------------------

    score = (
        rating_score * 0.50
        + budget_score * 0.30
        + duration_score * 0.20
    )

    return round(score, 3)


# -----------------------------------
# SIMILARITY SCORE
# -----------------------------------

def calculate_similarity_scores(
    recommendations,
    budget,
    preferred_duration
):
    """
    Calculate similarity between
    user preferences and destinations.
    """

    if recommendations.empty:
        return recommendations


    # --------------------------------
    # User Preferences
    # --------------------------------

    if preferred_duration is None:

        user_duration = (
            recommendations["duration"]
            .mean()
        )

    else:

        user_duration = preferred_duration


    if budget is None:

        user_budget = (
            recommendations["cost"]
            .mean()
        )

    else:

        user_budget = budget


    # --------------------------------
    # Features
    # --------------------------------

    features = recommendations[
        [
            "rating",
            "cost",
            "duration"
        ]
    ].copy()


    # --------------------------------
    # Normalize Destination Data
    # --------------------------------

    scaler = MinMaxScaler()

    normalized_features = (
        scaler.fit_transform(features)
    )


    # --------------------------------
    # User Preference Vector
    # --------------------------------

    user_vector = pd.DataFrame(
        [[
            5.0,
            user_budget,
            user_duration
        ]],
        columns=[
            "rating",
            "cost",
            "duration"
        ]
    )


    # --------------------------------
    # Normalize User Vector
    # --------------------------------

    feature_min = features.min()

    feature_max = features.max()

    denominator = (
        feature_max - feature_min
    ).replace(0, 1)

    normalized_user = (
        user_vector - feature_min
    ) / denominator


    # --------------------------------
    # Cosine Similarity
    # --------------------------------

    similarity = cosine_similarity(
        normalized_features,
        normalized_user
    ).flatten()


    recommendations = (
        recommendations.copy()
    )

    recommendations[
        "similarity"
    ] = similarity


    return recommendations


# -----------------------------------
# MAIN RECOMMENDATION FUNCTION
# -----------------------------------

def recommend_places(
    city,
    category=None,
    budget=None,
    min_rating=0,
    preferred_duration=None
):
    """
    Hybrid travel recommendation system.

    Uses:
    - City filtering
    - Category filtering
    - Rating filtering
    - Weighted scoring
    - Feature normalization
    - Cosine similarity
    - Hybrid ranking
    """

    # --------------------------------
    # LOAD DATASET
    # --------------------------------

    places = load_places()


    # --------------------------------
    # CITY FILTER
    # --------------------------------

    recommendations = places[
        places["city"].str.lower()
        == city.lower()
    ].copy()


    # --------------------------------
    # CATEGORY FILTER
    # --------------------------------

    if category:

        recommendations = (
            recommendations[
                recommendations["category"]
                .str.lower()
                == category.lower()
            ].copy()
        )


    # --------------------------------
    # RATING FILTER
    # --------------------------------

    recommendations = (
        recommendations[
            recommendations["rating"]
            >= min_rating
        ].copy()
    )


    # --------------------------------
    # EMPTY CHECK
    # --------------------------------

    if recommendations.empty:

        return recommendations


    # --------------------------------
    # RULE-BASED SCORE
    # --------------------------------

    recommendations["score"] = (
        recommendations.apply(
            lambda row:
            calculate_score(
                row,
                budget,
                preferred_duration
            ),
            axis=1
        )
    )


    # --------------------------------
    # SIMILARITY
    # --------------------------------

    recommendations = (
        calculate_similarity_scores(
            recommendations,
            budget,
            preferred_duration
        )
    )


    # --------------------------------
    # HYBRID FINAL SCORE
    # --------------------------------

    recommendations[
        "final_score"
    ] = (
        recommendations["score"] * 0.60
        +
        recommendations["similarity"] * 0.40
    )


    # --------------------------------
    # SORT
    # --------------------------------

    recommendations = (
        recommendations.sort_values(
            by="final_score",
            ascending=False
        )
    )


    # --------------------------------
    # RESET INDEX
    # --------------------------------

    recommendations = (
        recommendations.reset_index(
            drop=True
        )
    )


    return recommendations