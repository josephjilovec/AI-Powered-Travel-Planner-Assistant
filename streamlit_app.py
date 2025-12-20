"""
Main Streamlit application entry point for AI-Powered Travel Planner Assistant.

This is the production-ready entry point optimized for Streamlit Cloud deployment.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

# Add current directory to path for imports
# This ensures components and utils can be imported
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from components.ui_components import (
    render_about_page,
    render_error_message,
    render_header,
    render_itinerary,
    render_loading_state,
    render_navigation,
    render_preferences_summary,
    render_recommendations,
    render_trip_form,
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import after path setup
try:
    from config import get_config
    from src.orchestrator import TravelPlannerOrchestrator
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

# Page configuration - Mobile optimized
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",  # Collapsed for mobile users
)

# Custom CSS for professional appearance and mobile responsiveness
st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3rem;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2c3e50;
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
    }
    
    /* Better spacing for mobile */
    @media (max-width: 768px) {
        .element-container {
            width: 100% !important;
            padding-bottom: 0.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_orchestrator() -> TravelPlannerOrchestrator:
    """
    Get or create the travel planner orchestrator (cached).

    Returns:
        TravelPlannerOrchestrator instance.
    """
    logger.info("Initializing Travel Planner Orchestrator (cached)")
    return TravelPlannerOrchestrator()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def plan_trip_cached(
    destination: str,
    user_input: str,
    duration: int,
    start_date: Optional[str],
    budget: Optional[float],
    additional_preferences: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Cache trip planning results.

    Args:
        destination: Travel destination.
        user_input: User preferences text.
        duration: Trip duration.
        start_date: Start date.
        budget: Budget amount.
        additional_preferences: Additional preferences.

    Returns:
        Trip planning results.
    """
    orchestrator = get_orchestrator()
    return orchestrator.plan_trip(
        destination=destination,
        user_input=user_input,
        duration=duration,
        start_date=start_date,
        budget=budget,
        additional_preferences=additional_preferences,
    )


def main() -> None:
    """Main application function."""
    try:
        # Validate configuration
        config = get_config()
        config.validate()

        # Show demo mode banner if applicable
        if config.demo_mode:
            st.info(
                "🎭 **DEMO MODE**: This application is running with mock/demo data. "
                "To use real AI features, configure your GEMINI_API_KEY in Streamlit secrets "
                "or set DEMO_MODE=false. The demo showcases the UI and workflow with sample data."
            )

        # Render header
        render_header()

        # Render navigation at top (mobile-friendly)
        current_page = render_navigation()

        # Initialize session state
        if "trip_data" not in st.session_state:
            st.session_state.trip_data = None

        if "current_step" not in st.session_state:
            st.session_state.current_step = "form"

        # Route to appropriate page
        if current_page == "Plan Trip":
            render_plan_trip_page()
        elif current_page == "View Itinerary":
            render_view_itinerary_page()
        elif current_page == "About":
            render_about_page()

    except ValueError as e:
        # In demo mode, we should not raise this error
        config = get_config()
        if not config.demo_mode:
            st.error(f"Configuration Error: {str(e)}")
            st.info(
                "Please configure your GEMINI_API_KEY in Streamlit secrets "
                "(for Streamlit Cloud) or as an environment variable (for local development). "
                "Alternatively, set DEMO_MODE=true to use demo data."
            )
            logger.error(f"Configuration error: {e}", exc_info=True)
        else:
            # Demo mode is active, continue
            pass

    except Exception as e:
        render_error_message(e)
        logger.error(f"Unexpected error: {e}", exc_info=True)


def render_plan_trip_page() -> None:
    """Render the trip planning page."""
    st.header("Plan Your Trip")

    # Render form
    form_data = render_trip_form()

    # Process form submission
    if form_data["submit"]:
        # Validate required fields - UX Safety Feature
        if not form_data["destination"] or not form_data["destination"].strip():
            st.warning("⚠️ Please enter a destination to begin!")
            return

        if not form_data["user_input"] and not form_data["interests"]:
            st.warning(
                "⚠️ Please provide some information about your preferences or interests."
            )
            return

        # Prepare additional preferences from form
        additional_preferences = {}
        if form_data["travel_style"]:
            additional_preferences["travel_style"] = form_data["travel_style"]
        if form_data["accommodation"]:
            additional_preferences["accommodation_type"] = form_data["accommodation"]
        if form_data["interests"]:
            additional_preferences["interests"] = form_data["interests"]
        if form_data["dietary"]:
            additional_preferences["dietary_restrictions"] = form_data["dietary"]

        # Combine user input with structured data
        user_input = form_data["user_input"]
        if not user_input:
            # Build user input from structured data
            user_input = "Interests: " + ", ".join(form_data["interests"])
            if form_data["travel_style"]:
                user_input += f". Travel style: {form_data['travel_style']}"
            if form_data["accommodation"]:
                user_input += f". Accommodation: {form_data['accommodation']}"
            if form_data["dietary"]:
                user_input += f". Dietary: {', '.join(form_data['dietary'])}"

        # Show loading state - UX Safety Feature
        try:
            with st.spinner("🤖 Generating your custom itinerary... This may take a moment."):
                # Plan trip
                trip_data = plan_trip_cached(
                    destination=form_data["destination"],
                    user_input=user_input,
                    duration=form_data["duration"],
                    start_date=form_data["start_date"].strftime("%Y-%m-%d")
                    if form_data["start_date"]
                    else None,
                    budget=form_data["budget"],
                    additional_preferences=additional_preferences,
                )

                # Store in session state
                st.session_state.trip_data = trip_data
                st.session_state.current_step = "results"

                # Success cues - UX Safety Feature
                st.success("✅ Itinerary Ready!")
                st.balloons()  # Celebration animation

                # Render results
                render_trip_results(trip_data)

        except Exception as e:
            # Friendly error message - UX Safety Feature
            st.error("😅 Oops! The travel spirits are busy. Please try again in a moment.")
            st.info("If this problem persists, check your internet connection or try again later.")
            logger.error(f"Error planning trip: {e}", exc_info=True)

    # Show existing results if available
    elif st.session_state.trip_data and st.session_state.current_step == "results":
        render_trip_results(st.session_state.trip_data)


def render_trip_results(trip_data: Dict[str, Any]) -> None:
    """
    Render trip planning results.

    Args:
        trip_data: Trip data dictionary.
    """
    if not trip_data or not trip_data.get("success"):
        st.warning("No trip data available.")
        return

    # Preferences summary
    if trip_data.get("preferences"):
        render_preferences_summary(trip_data["preferences"])

    st.divider()

    # Recommendations
    if trip_data.get("recommendations_result"):
        render_recommendations(trip_data["recommendations_result"])

    st.divider()

    # Itinerary
    if trip_data.get("itinerary_result"):
        render_itinerary(trip_data["itinerary_result"])


def render_view_itinerary_page() -> None:
    """Render the view itinerary page."""
    st.header("View Itinerary")

    if st.session_state.trip_data and st.session_state.trip_data.get("success"):
        render_itinerary(st.session_state.trip_data["itinerary_result"])
    else:
        st.info(
            "No itinerary available. Please plan a trip first using the 'Plan Trip' page."
        )


if __name__ == "__main__":
    main()

