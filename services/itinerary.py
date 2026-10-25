import math
import pandas as pd


# -----------------------------------
# DISTANCE CALCULATION
# -----------------------------------

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate approximate geographical distance
    between two locations using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# -----------------------------------
# FIND DISTANCE BETWEEN PLACES
# -----------------------------------

def distance_between_places(
    place1,
    place2
):
    """
    Calculate distance between two places.
    """

    return calculate_distance(
        place1["latitude"],
        place1["longitude"],
        place2["latitude"],
        place2["longitude"]
    )


# -----------------------------------
# CREATE SMART ITINERARY
# -----------------------------------

def create_itinerary(
    recommendations,
    days
):
    """
    Create a smart day-wise itinerary.

    The algorithm considers:
    - Recommendation score
    - Duration
    - Geographical location
    - Number of travel days
    """

    if recommendations.empty:
        return {}

    # Make a copy
    places = recommendations.copy()

    # Make sure days is an integer
    days = int(days)

    if days <= 0:
        return {}

    # -----------------------------------
    # LIMIT DAYS TO AVAILABLE PLACES
    # -----------------------------------

    days = min(days, len(places))

    # -----------------------------------
    # SORT BY RECOMMENDATION SCORE
    # -----------------------------------

    if "final_score" in places.columns:

        places = places.sort_values(
            by="final_score",
            ascending=False
        )

    elif "score" in places.columns:

        places = places.sort_values(
            by="score",
            ascending=False
        )

    else:

        places = places.sort_values(
            by="rating",
            ascending=False
        )

    places = places.reset_index(drop=True)

    # -----------------------------------
    # CREATE EMPTY DAYS
    # -----------------------------------

    itinerary = {}

    for day in range(1, days + 1):

        itinerary[day] = {
            "places": [],
            "total_duration": 0,
            "total_cost": 0
        }

    # -----------------------------------
    # MAXIMUM SIGHTSEEING HOURS
    # -----------------------------------

    max_hours_per_day = 8

    # -----------------------------------
    # FIRST PLACE OF EACH DAY
    # -----------------------------------

    # Put the highest-ranked places
    # as starting points for each day.

    for day in range(1, days + 1):

        if len(places) == 0:
            break

        place = places.iloc[0]

        places = places.iloc[1:].reset_index(drop=True)

        itinerary[day]["places"].append(place.to_dict())

        itinerary[day]["total_duration"] += place["duration"]

        itinerary[day]["total_cost"] += place["cost"]

    # -----------------------------------
    # ASSIGN REMAINING PLACES
    # -----------------------------------

    for _, place in places.iterrows():

        best_day = None
        best_score = float("inf")

        for day in range(1, days + 1):

            current_places = itinerary[day]["places"]

            current_duration = (
                itinerary[day]["total_duration"]
            )

            # -----------------------------------
            # Duration constraint
            # -----------------------------------

            if (
                current_duration
                + place["duration"]
                > max_hours_per_day
            ):

                continue

            # -----------------------------------
            # Calculate location score
            # -----------------------------------

            if current_places:

                distances = []

                for existing_place in current_places:

                    distance = distance_between_places(
                        existing_place,
                        place
                    )

                    distances.append(distance)

                average_distance = (
                    sum(distances)
                    / len(distances)
                )

            else:

                average_distance = 0

            # -----------------------------------
            # Duration balance
            # -----------------------------------

            duration_score = current_duration

            # -----------------------------------
            # Combined assignment score
            # -----------------------------------

            assignment_score = (
                average_distance * 0.7
                +
                duration_score * 0.3
            )

            if assignment_score < best_score:

                best_score = assignment_score
                best_day = day

        # -----------------------------------
        # If no day has enough time
        # -----------------------------------

        if best_day is None:

            # Put the place in the day
            # having the least duration.

            best_day = min(
                itinerary,
                key=lambda d:
                itinerary[d]["total_duration"]
            )

        # -----------------------------------
        # Add place to selected day
        # -----------------------------------

        itinerary[best_day]["places"].append(
            place.to_dict()
        )

        itinerary[best_day]["total_duration"] += (
            place["duration"]
        )

        itinerary[best_day]["total_cost"] += (
            place["cost"]
        )

    # -----------------------------------
    # FINAL CLEAN ITINERARY
    # -----------------------------------

    final_itinerary = {}

    for day, data in itinerary.items():

        final_itinerary[day] = data["places"]

    return final_itinerary


# -----------------------------------
# DISPLAY ITINERARY
# -----------------------------------

def display_itinerary(itinerary):
    """
    Display itinerary in the terminal.
    """

    print("\n===================================")
    print("       YOUR TRAVEL ITINERARY")
    print("===================================")

    if not itinerary:

        print(
            "No itinerary could be created."
        )

        return

    for day, places in itinerary.items():

        print(f"\nDAY {day}")

        print(
            "-----------------------------------"
        )

        for i, place in enumerate(
            places,
            start=1
        ):

            print(
                f"{i}. {place['name']}"
                f" | {place['category']}"
                f" | Rating: {place['rating']}"
                f" | Cost: ₹{place['cost']}"
                f" | Duration: "
                f"{place['duration']} hrs"
            )