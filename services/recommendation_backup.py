import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


def load_places():
    """
    Load travel places from CSV.
    """
    return pd.read_csv("data/places.csv")


def calculate_score(row, budget, preferred_duration=None):
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

            budget_score = 1 - (cost / budget) * 0.3

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
            row["duration"] - preferred_duration
        )

        duration_score = max(
            0,
            1 - (
                difference / preferred_duration
            )
        )

    # --------------------------------
    # Final Score
    # --------------------------------

    score = (
        rating_score * 0.50
        + budget_score * 0.30
        + duration_score * 0.20
    )

    return round(score, 3)


def calculate_similarity_scores(
    recommendations,
    budget,
    preferred_duration
):
    """
    Calculate similarity between user preferences
    and available destinations.
    """

    if recommendations.empty:
        return recommendations

    # --------------------------------
    # Create user preference vector
    # --------------------------------

    user_duration = (
        preferred_duration
        if preferred_duration is not None
        else recommendations["duration"].mean()
    )

    user_budget = (
        budget
        if budget is not None
        else recommendations["cost"].mean()
    )

    # --------------------------------
    # Features used for similarity
    # --------------------------------

    features = recommendations[
        [
            "rating",
            "cost",
            "duration"
        ]
    ].copy()

    # --------------------------------
    # Normalize destination data
    # --------------------------------

    scaler = MinMaxScaler()

    normalized_features = scaler.fit_transform(
        features
    )

    # --------------------------------
    # Normalize user preferences
    # --------------------------------

    feature_min = features.min()
    feature_max = features.max()

    user_rating = 5.0

    user_vector = pd.DataFrame(
        [[
            user_rating,
            user_budget,
            user_duration
        ]],
        columns=[
            "rating",
            "cost",
            "duration"
        ]
    )

    # Prevent division problems
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

    recommendations = recommendations.copy()

    recommendations["similarity"] = similarity

    return recommendations


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
    - Filtering
    - Preference similarity
    - Weighted recommendation score
    """

    # --------------------------------
    # Load Dataset
    # --------------------------------

    places = load_places()

    # --------------------------------
    # City Filter
    # --------------------------------

    recommendations = places[
        places["city"].str.lower()
        == city.lower()
    ].copy()

    # --------------------------------
    # Category Filter
    # --------------------------------

    if category:

        recommendations = recommendations[
            recommendations["category"].str.lower()
            == category.lower()
        ].copy()

    # --------------------------------
    # Rating Filter
    # --------------------------------

    recommendations = recommendations[
        recommendations["rating"] >= min_rating
    ].copy()

    # --------------------------------
    # Check Empty Dataset
    # --------------------------------

    if recommendations.empty:
        return recommendations

    # --------------------------------
    # Existing Recommendation Score
    # --------------------------------

    recommendations["score"] = recommendations.apply(
        lambda row: calculate_score(
            row,
            budget,
            preferred_duration
        ),
        axis=1
    )

    # --------------------------------
    # Similarity Score
    # --------------------------------

    recommendations = calculate_similarity_scores(
        recommendations,
        budget,
        preferred_duration
    )

    # --------------------------------
    # Hybrid Score
    # --------------------------------

    recommendations["final_score"] = (
        recommendations["score"] * 0.6
        + recommendations["similarity"] * 0.4
    )

    # --------------------------------
    # Sort Recommendations
    # --------------------------------

    recommendations = recommendations.sort_values(
        by="final_score",
        ascending=False
    )

    # --------------------------------
    # Reset Index
    # --------------------------------

    recommendations = recommendations.reset_index(
        drop=True
    )

    return recommendations