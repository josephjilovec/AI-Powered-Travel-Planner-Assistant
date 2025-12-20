"""
Search Agent for AI-Powered Travel Planner Assistant.

Searches for travel destinations, activities, and recommendations based on preferences.
"""

from typing import Any, Dict, List

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.mock_data import get_mock_recommendations

logger = get_logger(__name__)


class SearchAgent(BaseAgent):
    """Agent responsible for searching and recommending travel options."""

    def __init__(self) -> None:
        """Initialize the Search Agent."""
        super().__init__("Search")
        self.system_prompt = """You are a travel search and recommendation agent.
Your task is to provide detailed travel recommendations based on user preferences and destination.

For the given destination and preferences, provide:
1. Top attractions and activities
2. Recommended accommodations (with general price ranges)
3. Dining recommendations (considering dietary restrictions)
4. Transportation options
5. Best time to visit
6. Cultural tips and local customs
7. Budget considerations

Format your response as a structured list with clear sections.
Be specific, practical, and consider the user's travel style and interests.
Provide realistic recommendations that match the user's preferences."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for travel recommendations.

        Args:
            input_data: Dictionary containing:
                - 'destination': Destination name
                - 'preferences': User preferences dictionary
                - 'duration': Trip duration in days (optional)
                - 'budget': Budget amount (optional)

        Returns:
            Dictionary with search results and recommendations.

        Raises:
            ValueError: If input_data is missing required keys.
            RuntimeError: If search fails.
        """
        try:
            required_keys = ["destination", "preferences"]
            for key in required_keys:
                if key not in input_data:
                    raise ValueError(f"input_data must contain '{key}' key")

            destination = str(input_data["destination"])
            preferences = input_data["preferences"]
            duration = input_data.get("duration", "not specified")
            budget = input_data.get("budget")

            logger.info(f"Searching recommendations for destination: {destination}")

            # Check if in demo mode
            if self.config.demo_mode or self.api_client is None:
                logger.info("Using mock data for recommendations (demo mode)")
                recommendations = get_mock_recommendations(destination, preferences)
                response_text = recommendations.get("full_text", "")
            else:
                # Build user input
                user_input = f"Destination: {destination}\n"
                user_input += f"Trip Duration: {duration} days\n"

                if budget:
                    user_input += f"Budget: ${budget:,.2f}\n"

                user_input += f"\nPreferences:\n"
                if isinstance(preferences, dict):
                    for key, value in preferences.items():
                        if value:
                            user_input += f"- {key}: {value}\n"

                prompt = self._create_prompt(self.system_prompt, user_input)

                # Generate response
                response_text = self.api_client.generate_content(
                    prompt, temperature=0.7  # Higher temperature for creative recommendations
                )

                # Parse and structure response
                recommendations = self._parse_recommendations(response_text, destination)

            logger.info(f"Successfully generated recommendations for {destination}")
            return {
                "success": True,
                "destination": destination,
                "recommendations": recommendations,
                "raw_response": response_text,
            }

        except Exception as e:
            logger.error(f"Error processing search: {e}", exc_info=True)
            raise RuntimeError(f"Failed to search recommendations: {e}") from e

    def _parse_recommendations(
        self, response_text: str, destination: str
    ) -> Dict[str, Any]:
        """
        Parse recommendations from API response.

        Args:
            response_text: Raw API response.
            destination: Destination name.

        Returns:
            Structured recommendations dictionary.
        """
        # Structure the response into categories
        recommendations = {
            "destination": destination,
            "attractions": [],
            "accommodations": [],
            "dining": [],
            "transportation": [],
            "tips": [],
            "full_text": response_text,
        }

        # Simple parsing - extract sections if they exist
        lines = response_text.split("\n")
        current_section = None

        for line in lines:
            line_lower = line.lower().strip()
            if "attraction" in line_lower or "activity" in line_lower:
                current_section = "attractions"
            elif "accommodation" in line_lower or "hotel" in line_lower or "stay" in line_lower:
                current_section = "accommodations"
            elif "dining" in line_lower or "restaurant" in line_lower or "food" in line_lower:
                current_section = "dining"
            elif "transport" in line_lower or "getting around" in line_lower:
                current_section = "transportation"
            elif "tip" in line_lower or "custom" in line_lower:
                current_section = "tips"
            elif line.strip() and current_section:
                # Add line to current section if it's not empty
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    recommendations[current_section].append(line.strip()[1:].strip())

        return recommendations

