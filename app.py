import streamlit as st
import pandas as pd

from services.recommendation import recommend_places
from services.itinerary import create_itinerary
from services.budget import calculate_total_budget
from services.hotel import recommend_hotels
from services.transport import recommend_transport
from services.route import optimize_route

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Smart Travel Roadmap",
    page_icon="🌍",
    layout="wide"
)


# -----------------------------------
# TITLE
# -----------------------------------

st.title("🌍 Smart Travel Roadmap")

st.write(
    "AI-powered travel planning system"
)


# -----------------------------------
# USER INPUT
# -----------------------------------

city = st.selectbox(
    "Select Destination",
    ["Goa"]
)

category = st.selectbox(
    "Select Travel Category",
    [
        "Beach",
        "Nature",
        "Historical"
    ]
)

days = st.number_input(
    "Number of Days",
    min_value=1,
    max_value=30,
    value=3
)

people = st.number_input(
    "Number of People",
    min_value=1,
    max_value=20,
    value=2
)

budget = st.number_input(
    "Total Budget (₹)",
    min_value=500,
    value=10000,
    step=500
)


# -----------------------------------
# GENERATE BUTTON
# -----------------------------------

if st.button("✨ Generate Travel Roadmap"):

    st.header("✨ Your Travel Roadmap")

    # -----------------------------------
    # RECOMMENDATION
    # -----------------------------------

    results = recommend_places(
        city=city,
        category=category,
        budget=budget,
        min_rating=4.0,
        preferred_duration=3
    )

    if results.empty:

        st.warning(
            "No suitable places found."
        )

    else:

        # -----------------------------------
        # RECOMMENDATIONS
        # -----------------------------------

        st.subheader(
            "🏖️ Recommended Places"
        )

        st.info(
            "Places are ranked using rating, "
            "budget suitability and visit duration."
        )

        st.dataframe(
            results[
                [
                    "name",
                    "category",
                    "rating",
                    "cost",
                    "duration",
                    "score"
                ]
            ],
            use_container_width=True
        )


        # -----------------------------------
        # ITINERARY
        # -----------------------------------

        itinerary = create_itinerary(
            results,
            days
        )

                # -----------------------------------
        # ITINERARY + ROUTE
        # -----------------------------------

        st.subheader(
            "📅 Day-wise Itinerary"
        )

        for day, places in itinerary.items():

            st.write(
                f"### Day {day}"
            )

            # Optimize route for this day
            optimized_route, distance = optimize_route(
                places
            )

            st.write(
                f"🛣️ Total Route Distance: "
                f"{distance} km"
            )

            for index, place in enumerate(
                optimized_route,
                start=1
            ):

                st.write(
                    f"{index}. 📍 {place['name']} "
                    f"⭐ {place['rating']} "
                    f"⏱️ {place['duration']} hrs"
                )
    st.write(
        f"🛣️ Total Route Distance: "
        f"{distance} km"
    )

    for index, place in enumerate(
        optimized_route,
        start=1
    ):

        st.write(
            f"{index}. 📍 {place['name']} "
            f"⭐ {place['rating']} "
            f"⏱️ {place['duration']} hrs"
        )

        # -----------------------------------
        # HOTEL RECOMMENDATION
        # -----------------------------------

        hotel_budget = budget / 3

        hotels = recommend_hotels(
            city=city,
            max_price=hotel_budget,
            min_rating=4.0
        )

        if hotels.empty:

            st.warning(
                "No suitable hotel found within "
                "the selected budget."
            )

            # Default hotel price
            hotel_price = 2000

        else:

            selected_hotel = hotels.iloc[0]

            hotel_price = selected_hotel[
                "price_per_night"
            ]

            st.subheader(
                "🏨 Recommended Hotel"
            )

            st.write(
                f"**{selected_hotel['name']}**"
            )

            st.write(
                f"⭐ Rating: "
                f"{selected_hotel['rating']}"
            )

            st.write(
                f"💰 ₹{selected_hotel['price_per_night']} "
                f"/ night"
            )


        # -----------------------------------
        # TRANSPORT
        # -----------------------------------

        transport_cost = 1000


        # -----------------------------------
        # BUDGET CALCULATION
        # -----------------------------------

        budget_details = calculate_total_budget(
            places=results,
            days=days,
            people=people,
            hotel_price=hotel_price,
            transport_cost=transport_cost
        )


        # -----------------------------------
        # BUDGET DISPLAY
        # -----------------------------------

        st.subheader(
            "💰 Estimated Budget"
        )

        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Places",
            f"₹{budget_details['places']}"
        )


        col2.metric(
            "Food",
            f"₹{budget_details['food']}"
        )


        col3.metric(
            "Hotel",
            f"₹{budget_details['hotel']}"
        )


        col4.metric(
            "Transport",
            f"₹{budget_details['transport']}"
        )


        st.success(
            f"Estimated Total: "
            f"₹{budget_details['total']}"
        )