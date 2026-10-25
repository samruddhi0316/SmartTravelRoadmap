import pandas as pd


def load_hotels():
    """
    Load hotel data from CSV.
    """
    return pd.read_csv("data/hotels.csv")


def recommend_hotels(
    city,
    max_price=None,
    min_rating=0
):
    """
    Recommend hotels based on city,
    price and rating.
    """

    hotels = load_hotels()

    # City filter
    hotels = hotels[
        hotels["city"].str.lower() == city.lower()
    ].copy()

    # Rating filter
    hotels = hotels[
        hotels["rating"] >= min_rating
    ].copy()

    # Price filter
    if max_price is not None:
        hotels = hotels[
            hotels["price_per_night"] <= max_price
        ].copy()

    # Highest-rated hotels first
    hotels = hotels.sort_values(
        by="rating",
        ascending=False
    )

    return hotels.reset_index(drop=True)