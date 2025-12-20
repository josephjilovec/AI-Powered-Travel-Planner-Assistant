"""
UI components for Streamlit application.

Provides reusable UI components for the travel planner interface.
"""

from typing import Any, Dict, List, Optional

import streamlit as st

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


def render_header() -> None:
    """Render the application header."""
    st.title("✈️ AI-Powered Travel Planner Assistant")
    st.markdown(
        """
        <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
            <p style='font-size: 1.1em;'>
                Plan your perfect trip with AI-powered recommendations and personalized itineraries
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with navigation and settings.

    Returns:
        Dictionary with sidebar state.
    """
    with st.sidebar:
        st.header("🗺️ Navigation")
        page = st.radio(
            "Select Page",
            ["Plan Trip", "View Itinerary", "About"],
            key="navigation",
        )

        st.divider()

        st.header("⚙️ Settings")
        temperature = st.slider(
            "AI Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values = more creative, Lower values = more focused",
        )

        st.divider()

        st.markdown(
            """
            <div style='text-align: center; color: #888; font-size: 0.9em;'>
                <p>Powered by Google Gemini AI</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {"page": page, "temperature": temperature}


def render_trip_form() -> Dict[str, Any]:
    """
    Render the trip planning form.

    Returns:
        Dictionary with form data.
    """
    st.header("📝 Trip Details")

    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input(
            "Destination",
            placeholder="e.g., Paris, France",
            help="Enter your travel destination",
        )

        start_date = st.date_input(
            "Start Date",
            help="When does your trip begin?",
        )

    with col2:
        duration = st.number_input(
            "Duration (days)",
            min_value=1,
            max_value=365,
            value=7,
            help="How many days is your trip?",
        )

        budget = st.number_input(
            "Budget (USD)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="Optional: Enter your budget (0 = no budget specified)",
        )

    st.divider()

    st.subheader("🎯 Your Preferences")
    st.markdown(
        "Tell us about your travel style, interests, and any special requirements:"
    )

    user_input = st.text_area(
        "Describe your preferences",
        placeholder=(
            "e.g., I love museums, art galleries, and fine dining. "
            "I prefer luxury accommodations and I'm vegetarian. "
            "I'm interested in history and culture."
        ),
        height=150,
        help="Describe your interests, travel style, dietary restrictions, etc.",
    )

    col1, col2 = st.columns(2)

    with col1:
        travel_style = st.selectbox(
            "Travel Style",
            ["", "Budget", "Mid-range", "Luxury", "Adventure", "Relaxation", "Family"],
            help="What's your preferred travel style?",
        )

        accommodation = st.selectbox(
            "Accommodation Type",
            [
                "",
                "Hotel",
                "Hostel",
                "Airbnb",
                "Resort",
                "Boutique Hotel",
                "No preference",
            ],
            help="What type of accommodation do you prefer?",
        )

    with col2:
        interests = st.multiselect(
            "Interests",
            [
                "Museums",
                "Art Galleries",
                "Beaches",
                "Mountains",
                "Nightlife",
                "Shopping",
                "Food & Dining",
                "History",
                "Nature",
                "Adventure Sports",
                "Religious Sites",
                "Architecture",
            ],
            help="Select your interests (can select multiple)",
        )

        dietary = st.multiselect(
            "Dietary Restrictions",
            [
                "None",
                "Vegetarian",
                "Vegan",
                "Halal",
                "Kosher",
                "Gluten-free",
                "Dairy-free",
                "Nut allergy",
            ],
            help="Any dietary restrictions or preferences?",
        )

    submit_button = st.button("🚀 Plan My Trip", type="primary", use_container_width=True)

    return {
        "destination": destination,
        "start_date": start_date,
        "duration": duration,
        "budget": budget if budget > 0 else None,
        "user_input": user_input,
        "travel_style": travel_style,
        "accommodation": accommodation,
        "interests": interests,
        "dietary": dietary,
        "submit": submit_button,
    }


def render_preferences_summary(preferences: Dict[str, Any]) -> None:
    """
    Render a summary of extracted preferences.

    Args:
        preferences: Preferences dictionary.
    """
    st.subheader("✅ Extracted Preferences")

    if not preferences:
        st.info("No preferences extracted yet.")
        return

    cols = st.columns(3)

    with cols[0]:
        if preferences.get("interests"):
            st.markdown("**Interests:**")
            for interest in preferences["interests"]:
                st.markdown(f"- {interest}")

    with cols[1]:
        if preferences.get("travel_style"):
            st.markdown("**Travel Style:**")
            st.markdown(f"- {preferences['travel_style']}")

        if preferences.get("accommodation_type"):
            st.markdown("**Accommodation:**")
            st.markdown(f"- {preferences['accommodation_type']}")

    with cols[2]:
        if preferences.get("dietary_restrictions"):
            st.markdown("**Dietary Restrictions:**")
            for restriction in preferences["dietary_restrictions"]:
                st.markdown(f"- {restriction}")


def render_recommendations(recommendations: Dict[str, Any]) -> None:
    """
    Render travel recommendations.

    Args:
        recommendations: Recommendations dictionary.
    """
    st.subheader(f"🌟 Recommendations for {recommendations.get('destination', 'Destination')}")

    if "recommendations" not in recommendations:
        st.warning("No recommendations available.")
        return

    recs = recommendations["recommendations"]

    tabs = st.tabs(["Attractions", "Accommodations", "Dining", "Transportation", "Tips"])

    with tabs[0]:
        if recs.get("attractions"):
            for attraction in recs["attractions"]:
                st.markdown(f"• {attraction}")
        else:
            st.info("No specific attractions listed. Check the full recommendations below.")

    with tabs[1]:
        if recs.get("accommodations"):
            for accommodation in recs["accommodations"]:
                st.markdown(f"• {accommodation}")
        else:
            st.info("No specific accommodations listed. Check the full recommendations below.")

    with tabs[2]:
        if recs.get("dining"):
            for restaurant in recs["dining"]:
                st.markdown(f"• {restaurant}")
        else:
            st.info("No specific dining options listed. Check the full recommendations below.")

    with tabs[3]:
        if recs.get("transportation"):
            for transport in recs["transportation"]:
                st.markdown(f"• {transport}")
        else:
            st.info("No specific transportation options listed.")

    with tabs[4]:
        if recs.get("tips"):
            for tip in recs["tips"]:
                st.markdown(f"• {tip}")
        else:
            st.info("No specific tips provided.")

    # Full recommendations in expander
    with st.expander("📄 View Full Recommendations"):
        st.markdown(recs.get("full_text", "No full text available."))


def render_itinerary(itinerary_data: Dict[str, Any]) -> None:
    """
    Render the travel itinerary.

    Args:
        itinerary_data: Itinerary dictionary.
    """
    if "itinerary" not in itinerary_data:
        st.warning("No itinerary available.")
        return

    st.subheader(
        f"📅 {itinerary_data.get('duration', 'N')}-Day Itinerary for "
        f"{itinerary_data.get('destination', 'Destination')}"
    )

    itinerary = itinerary_data["itinerary"]

    for day_data in itinerary:
        day_num = day_data.get("day", 1)
        date = day_data.get("date")

        with st.container():
            day_header = f"Day {day_num}"
            if date:
                day_header += f" - {date}"

            st.markdown(f"### {day_header}")

            col1, col2, col3 = st.columns(3)

            with col1:
                if day_data.get("morning"):
                    st.markdown("**🌅 Morning**")
                    for activity in day_data["morning"]:
                        st.markdown(f"• {activity}")

            with col2:
                if day_data.get("afternoon"):
                    st.markdown("**☀️ Afternoon**")
                    for activity in day_data["afternoon"]:
                        st.markdown(f"• {activity}")

            with col3:
                if day_data.get("evening"):
                    st.markdown("**🌙 Evening**")
                    for activity in day_data["evening"]:
                        st.markdown(f"• {activity}")

            if day_data.get("notes"):
                with st.expander("📝 Notes & Tips"):
                    for note in day_data["notes"]:
                        st.markdown(f"• {note}")

            st.divider()

    # Full itinerary in expander
    with st.expander("📄 View Full Itinerary Text"):
        st.markdown(itinerary_data.get("raw_response", "No full text available."))


def render_about_page() -> None:
    """Render the about page."""
    st.header("About AI-Powered Travel Planner Assistant")

    st.markdown(
        """
        ### Overview
        This application uses advanced AI to help you plan your perfect trip. 
        It leverages Google's Gemini AI to understand your preferences, search for 
        recommendations, and create detailed itineraries.

        ### How It Works
        1. **Preference Extraction**: Our AI analyzes your natural language input 
           to understand your travel preferences, interests, and requirements.

        2. **Smart Recommendations**: Based on your destination and preferences, 
           the AI searches for and recommends attractions, accommodations, dining, 
           and transportation options.

        3. **Itinerary Generation**: A detailed day-by-day itinerary is created, 
           considering your preferences, available time, and practical constraints.

        ### Features
        - 🎯 Intelligent preference extraction from natural language
        - 🌟 Personalized travel recommendations
        - 📅 Detailed day-by-day itineraries
        - 🍽️ Dietary restriction awareness
        - 💰 Budget consideration
        - ⏱️ Realistic time planning

        ### Technology
        - **Frontend**: Streamlit
        - **AI Engine**: Google Gemini API
        - **Architecture**: Modular, production-ready design

        ### Privacy
        Your data is processed securely and is not stored permanently. 
        API keys and sensitive information are managed through Streamlit secrets.

        ### Support
        For issues or questions, please refer to the project's GitHub repository.
        """
    )


def render_error_message(error: Exception) -> None:
    """
    Render an error message to the user.

    Args:
        error: Exception that occurred.
    """
    st.error(f"❌ An error occurred: {str(error)}")
    st.info(
        "Please check your API key configuration and try again. "
        "If the problem persists, check the logs for more details."
    )


def render_loading_state(message: str = "Processing...") -> None:
    """
    Render a loading state.

    Args:
        message: Loading message to display.
    """
    st.info(f"⏳ {message} Please wait while we process your request...")

