import math


# -----------------------------------
# HAVERSINE DISTANCE
# -----------------------------------

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate approximate distance between
    two geographical coordinates.

    Returns distance in kilometers.
    """

    R = 6371

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

    return R * c


# -----------------------------------
# DISTANCE BETWEEN TWO PLACES
# -----------------------------------

def distance_between_places(
    place1,
    place2
):
    """
    Calculate distance between
    two places.
    """

    return calculate_distance(
        place1["latitude"],
        place1["longitude"],
        place2["latitude"],
        place2["longitude"]
    )


# -----------------------------------
# FIND NEAREST PLACE
# -----------------------------------

def find_nearest_place(
    current_place,
    remaining_places
):
    """
    Find the nearest unvisited place
    from the current location.
    """

    nearest_place = None
    nearest_distance = float("inf")

    for place in remaining_places:

        distance = distance_between_places(
            current_place,
            place
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_place = place

    return nearest_place, nearest_distance


# -----------------------------------
# OPTIMIZE ROUTE
# -----------------------------------

def optimize_route(
    places
):
    """
    Create a route using the
    Nearest Neighbor algorithm.

    The algorithm repeatedly selects
    the nearest unvisited place.
    """

    if not places:

        return [], 0

    # Copy list
    remaining_places = [
        place.copy()
        for place in places
    ]

    # Start with first place
    current_place = remaining_places.pop(0)

    route = [
        current_place
    ]

    total_distance = 0

    # -----------------------------------
    # FIND NEAREST UNVISITED PLACE
    # -----------------------------------

    while remaining_places:

        nearest_place, distance = (
            find_nearest_place(
                current_place,
                remaining_places
            )
        )

        if nearest_place is None:
            break

        route.append(nearest_place)

        total_distance += distance

        remaining_places.remove(
            nearest_place
        )

        current_place = nearest_place

    return route, round(total_distance, 2)


# -----------------------------------
# CALCULATE ROUTE DISTANCE
# -----------------------------------

def calculate_route_distance(
    route
):
    """
    Calculate total distance of
    an existing route.
    """

    if len(route) < 2:

        return 0

    total_distance = 0

    for i in range(
        len(route) - 1
    ):

        total_distance += (
            distance_between_places(
                route[i],
                route[i + 1]
            )
        )

    return round(
        total_distance,
        2
    )