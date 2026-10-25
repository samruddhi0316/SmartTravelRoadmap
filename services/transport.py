import pandas as pd


def load_transport():
    """
    Load transport data.
    """
    return pd.read_csv("data/transport.csv")


def recommend_transport(
    city,
    max_price=None
):
    """
    Recommend transport options
    based on destination and price.
    """

    transport = load_transport()

    # Filter city
    transport = transport[
        transport["city"].str.lower()
        == city.lower()
    ].copy()

    # Filter price
    if max_price is not None:

        transport = transport[
            transport["cost"] <= max_price
        ].copy()

    # Cheapest options first
    transport = transport.sort_values(
        by="cost",
        ascending=True
    )

    return transport