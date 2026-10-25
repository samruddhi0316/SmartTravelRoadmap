import pandas as pd

def calculate_place_cost(places):
    """
    Calculate total cost of visiting all recommended places.
    """

    if places.empty:
        return 0

    return places["cost"].sum()


def calculate_food_cost(days, people=1):
    """
    Estimate food cost.

    Assumption:
    ₹500 per person per day.
    """

    food_per_person_per_day = 500

    return days * people * food_per_person_per_day


def calculate_hotel_cost(
    hotel_price_per_night,
    days,
    rooms=1
):
    """
    Calculate hotel cost.
    """

    nights = max(days - 1, 1)

    return hotel_price_per_night * nights * rooms


def calculate_transport_cost(
    transport_cost,
    people=1
):
    """
    Calculate transport cost.
    """

    return transport_cost * people


def calculate_total_budget(
    places,
    days,
    people,
    hotel_price,
    transport_cost
):
    """
    Calculate complete estimated trip budget.
    """

    place_cost = calculate_place_cost(places)

    food_cost = calculate_food_cost(
        days,
        people
    )

    hotel_cost = calculate_hotel_cost(
        hotel_price,
        days
    )

    transport_total = calculate_transport_cost(
        transport_cost,
        people
    )

    total = (
        place_cost
        + food_cost
        + hotel_cost
        + transport_total
    )

    return {
        "places": place_cost,
        "food": food_cost,
        "hotel": hotel_cost,
        "transport": transport_total,
        "total": total
    }


def check_budget(total_cost, user_budget):
    """
    Check whether the trip is within the user's budget.
    """

    difference = user_budget - total_cost

    if difference >= 0:

        return {
            "status": "Within Budget",
            "difference": difference
        }

    else:

        return {
            "status": "Over Budget",
            "difference": abs(difference)
        }

    import pandas as pd


def recommend_hotels(
    city,
    max_price=None,
    min_rating=0
):
    """
    Recommend hotels based on city,
    price and rating.
    """

    hotels = pd.read_csv("data/hotels.csv")

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

    # Best-rated hotels first
    hotels = hotels.sort_values(
        by="rating",
        ascending=False
    )

    return hotels