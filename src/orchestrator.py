"""
Orchestrator for AI-Powered Travel Planner Assistant.

Coordinates the flow between different agents to create a complete travel plan.
"""

from typing import Any, Dict, Optional

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.itinerary_agent import ItineraryAgent
from src.agents.preference_agent import PreferenceAgent
from src.agents.search_agent import SearchAgent
from utils.logger import get_logger
from utils.validators import (
    ValidationError,
    validate_budget,
    validate_destination,
    validate_duration,
    validate_preferences,
)

logger = get_logger(__name__)


class TravelPlannerOrchestrator:
    """Orchestrates the travel planning process using multiple AI agents."""

    def __init__(self) -> None:
        """Initialize the orchestrator with all agents."""
        self.preference_agent = PreferenceAgent()
        self.search_agent = SearchAgent()
        self.itinerary_agent = ItineraryAgent()
        logger.info("Travel Planner Orchestrator initialized")

    def plan_trip(
        self,
        destination: str,
        user_input: str,
        duration: int,
        start_date: Optional[str] = None,
        budget: Optional[float] = None,
        additional_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Plan a complete trip using all agents.

        Args:
            destination: Travel destination.
            user_input: Natural language description of preferences.
            duration: Trip duration in days.
            start_date: Optional start date.
            budget: Optional budget amount.
            additional_preferences: Optional additional structured preferences.

        Returns:
            Dictionary containing preferences, recommendations, and itinerary.

        Raises:
            ValidationError: If input validation fails.
            RuntimeError: If planning process fails.
        """
        try:
            # Validate inputs
            destination = validate_destination(destination)
            duration = validate_duration(duration)
            budget = validate_budget(budget)

            logger.info(f"Starting trip planning for {destination} ({duration} days)")

            # Step 1: Extract preferences
            logger.info("Step 1: Extracting preferences...")
            preferences_result = self._extract_preferences(
                user_input, additional_preferences
            )

            if not preferences_result.get("success"):
                logger.warning("Preference extraction had issues, continuing anyway")

            preferences = preferences_result.get("preferences", {})

            # Merge with additional preferences
            if additional_preferences:
                preferences = {**preferences, **additional_preferences}

            # Validate preferences
            preferences = validate_preferences(preferences)

            # Step 2: Get recommendations
            logger.info("Step 2: Getting recommendations...")
            recommendations_result = self._get_recommendations(
                destination, preferences, duration, budget
            )

            if not recommendations_result.get("success"):
                raise RuntimeError("Failed to get recommendations")

            recommendations = recommendations_result.get("recommendations", {})

            # Step 3: Create itinerary
            logger.info("Step 3: Creating itinerary...")
            itinerary_result = self._create_itinerary(
                destination, preferences, recommendations, duration, start_date
            )

            if not itinerary_result.get("success"):
                raise RuntimeError("Failed to create itinerary")

            itinerary = itinerary_result.get("itinerary", [])

            logger.info("Trip planning completed successfully")

            return {
                "success": True,
                "destination": destination,
                "duration": duration,
                "preferences": preferences,
                "recommendations": recommendations,
                "itinerary": itinerary,
                "preferences_result": preferences_result,
                "recommendations_result": recommendations_result,
                "itinerary_result": itinerary_result,
            }

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise

        except Exception as e:
            logger.error(f"Error in trip planning: {e}", exc_info=True)
            raise RuntimeError(f"Failed to plan trip: {e}") from e

    def _extract_preferences(
        self, user_input: str, additional_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract preferences from user input.

        Args:
            user_input: Natural language input.
            additional_preferences: Optional additional preferences to merge.

        Returns:
            Preferences result dictionary.
        """
        try:
            result = self.preference_agent.process({"user_input": user_input})

            # Merge with additional preferences if provided
            if additional_preferences and result.get("preferences"):
                result["preferences"] = {**result["preferences"], **additional_preferences}

            return result

        except Exception as e:
            logger.error(f"Error extracting preferences: {e}", exc_info=True)
            # Return fallback preferences
            return {
                "success": False,
                "preferences": additional_preferences or {},
                "error": str(e),
            }

    def _get_recommendations(
        self,
        destination: str,
        preferences: Dict[str, Any],
        duration: int,
        budget: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get travel recommendations.

        Args:
            destination: Travel destination.
            preferences: User preferences.
            duration: Trip duration.
            budget: Optional budget.

        Returns:
            Recommendations result dictionary.
        """
        try:
            return self.search_agent.process(
                {
                    "destination": destination,
                    "preferences": preferences,
                    "duration": duration,
                    "budget": budget,
                }
            )

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}", exc_info=True)
            raise

    def _create_itinerary(
        self,
        destination: str,
        preferences: Dict[str, Any],
        recommendations: Dict[str, Any],
        duration: int,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create travel itinerary.

        Args:
            destination: Travel destination.
            preferences: User preferences.
            recommendations: Travel recommendations.
            duration: Trip duration.
            start_date: Optional start date.

        Returns:
            Itinerary result dictionary.
        """
        try:
            return self.itinerary_agent.process(
                {
                    "destination": destination,
                    "preferences": preferences,
                    "recommendations": recommendations,
                    "duration": duration,
                    "start_date": start_date,
                }
            )

        except Exception as e:
            logger.error(f"Error creating itinerary: {e}", exc_info=True)
            raise

