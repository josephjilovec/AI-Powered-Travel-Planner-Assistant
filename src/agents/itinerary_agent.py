"""
Itinerary Agent for AI-Powered Travel Planner Assistant.

Creates detailed day-by-day travel itineraries based on preferences and recommendations.
"""

from typing import Any, Dict, List

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class ItineraryAgent(BaseAgent):
    """Agent responsible for creating detailed travel itineraries."""

    def __init__(self) -> None:
        """Initialize the Itinerary Agent."""
        super().__init__("Itinerary")
        self.system_prompt = """You are a travel itinerary planning agent.
Your task is to create a detailed, day-by-day travel itinerary based on destination, 
preferences, and available recommendations.

Create an itinerary that:
1. Is realistic and considers travel time between locations
2. Balances activities based on user preferences and travel style
3. Includes meal times and breaks
4. Considers opening hours and best times to visit attractions
5. Provides time estimates for each activity
6. Includes practical information (addresses, tips, etc.)

Format your response as a clear day-by-day schedule with:
- Day number and date (if provided)
- Morning, Afternoon, Evening activities
- Time estimates
- Location names
- Brief descriptions
- Any important notes or tips

Make the itinerary engaging, practical, and aligned with the user's interests."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a travel itinerary.

        Args:
            input_data: Dictionary containing:
                - 'destination': Destination name
                - 'preferences': User preferences dictionary
                - 'recommendations': Search agent recommendations
                - 'duration': Trip duration in days
                - 'start_date': Start date (optional)

        Returns:
            Dictionary with detailed itinerary.

        Raises:
            ValueError: If input_data is missing required keys.
            RuntimeError: If itinerary creation fails.
        """
        try:
            required_keys = ["destination", "preferences", "recommendations", "duration"]
            for key in required_keys:
                if key not in input_data:
                    raise ValueError(f"input_data must contain '{key}' key")

            destination = str(input_data["destination"])
            preferences = input_data["preferences"]
            recommendations = input_data["recommendations"]
            duration = int(input_data["duration"])
            start_date = input_data.get("start_date", "Not specified")

            logger.info(
                f"Creating {duration}-day itinerary for destination: {destination}"
            )

            # Build user input
            user_input = f"Destination: {destination}\n"
            user_input += f"Trip Duration: {duration} days\n"
            user_input += f"Start Date: {start_date}\n\n"

            user_input += "User Preferences:\n"
            if isinstance(preferences, dict):
                for key, value in preferences.items():
                    if value:
                        user_input += f"- {key}: {value}\n"

            user_input += "\nAvailable Recommendations:\n"
            if isinstance(recommendations, dict):
                if "full_text" in recommendations:
                    user_input += recommendations["full_text"]
                else:
                    user_input += str(recommendations)

            prompt = self._create_prompt(self.system_prompt, user_input)

            # Generate response
            response_text = self.api_client.generate_content(
                prompt, temperature=0.8  # Higher temperature for creative planning
            )

            # Parse itinerary
            itinerary = self._parse_itinerary(response_text, duration)

            logger.info(f"Successfully created {duration}-day itinerary")
            return {
                "success": True,
                "destination": destination,
                "duration": duration,
                "itinerary": itinerary,
                "raw_response": response_text,
            }

        except Exception as e:
            logger.error(f"Error creating itinerary: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create itinerary: {e}") from e

    def _parse_itinerary(self, response_text: str, duration: int) -> List[Dict[str, Any]]:
        """
        Parse itinerary from API response.

        Args:
            response_text: Raw API response.
            duration: Number of days.

        Returns:
            List of day dictionaries with activities.
        """
        itinerary = []
        lines = response_text.split("\n")

        current_day = None
        current_period = None
        current_activities = []

        for line in lines:
            line_stripped = line.strip()

            # Detect day markers
            if "day" in line_stripped.lower() and any(
                char.isdigit() for char in line_stripped
            ):
                # Save previous day if exists
                if current_day is not None:
                    itinerary.append(current_day)

                # Start new day
                day_num = self._extract_day_number(line_stripped)
                current_day = {
                    "day": day_num,
                    "date": self._extract_date(line_stripped),
                    "morning": [],
                    "afternoon": [],
                    "evening": [],
                    "notes": [],
                }
                current_period = None
                current_activities = []

            # Detect time periods
            elif any(
                period in line_stripped.lower()
                for period in ["morning", "afternoon", "evening", "night"]
            ):
                period_map = {
                    "morning": "morning",
                    "afternoon": "afternoon",
                    "evening": "evening",
                    "night": "evening",
                }
                for key, value in period_map.items():
                    if key in line_stripped.lower():
                        current_period = value
                        break

            # Add activity
            elif line_stripped and current_day is not None:
                if line_stripped.startswith("-") or line_stripped.startswith("*"):
                    activity = line_stripped[1:].strip()
                    if current_period and current_period in current_day:
                        current_day[current_period].append(activity)
                    else:
                        # Default to morning if no period specified
                        current_day["morning"].append(activity)
                elif "note" in line_stripped.lower() or "tip" in line_stripped.lower():
                    current_day["notes"].append(line_stripped)

        # Add last day
        if current_day is not None:
            itinerary.append(current_day)

        # Ensure we have the right number of days
        while len(itinerary) < duration:
            itinerary.append(
                {
                    "day": len(itinerary) + 1,
                    "date": None,
                    "morning": [],
                    "afternoon": [],
                    "evening": [],
                    "notes": [],
                }
            )

        return itinerary[:duration]  # Trim to exact duration

    def _extract_day_number(self, text: str) -> int:
        """Extract day number from text."""
        import re

        match = re.search(r"day\s*(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 1

    def _extract_date(self, text: str) -> str:
        """Extract date from text if present."""
        # Simple extraction - can be enhanced
        import re

        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",
            r"\d{2}/\d{2}/\d{4}",
            r"\d{1,2}\s+\w+\s+\d{4}",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return None

