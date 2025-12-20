"""
Preference Agent for AI-Powered Travel Planner Assistant.

Extracts and structures user travel preferences from natural language input.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent
from utils.mock_data import get_mock_preferences

logger = logging.getLogger(__name__)


class PreferenceAgent(BaseAgent):
    """Agent responsible for understanding user travel preferences."""

    def __init__(self) -> None:
        """Initialize the Preference Agent."""
        super().__init__("Preference")
        self.system_prompt = """You are a travel preference extraction agent. 
Your task is to analyze user input and extract structured travel preferences.

Extract the following information:
1. Interests (e.g., museums, beaches, nightlife, nature, history)
2. Travel style (e.g., budget, luxury, adventure, relaxation, family-friendly)
3. Accommodation preferences (e.g., hotel, hostel, Airbnb, resort)
4. Dietary restrictions or preferences (e.g., vegetarian, vegan, halal, allergies)
5. Special requirements (e.g., accessibility needs, pet-friendly)

Return your response as a JSON object with the following structure:
{
    "interests": ["interest1", "interest2"],
    "travel_style": "style",
    "accommodation_type": "type",
    "dietary_restrictions": ["restriction1"],
    "special_requirements": ["requirement1"],
    "additional_notes": "any additional relevant information"
}

If information is not provided, use null or empty arrays as appropriate.
Be concise and only extract information that is explicitly mentioned or clearly implied."""

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract preferences from user input.

        Args:
            input_data: Dictionary containing 'user_input' key with natural language text.

        Returns:
            Dictionary with extracted preferences.

        Raises:
            ValueError: If input_data is missing required keys.
            RuntimeError: If preference extraction fails.
        """
        try:
            if "user_input" not in input_data:
                raise ValueError("input_data must contain 'user_input' key")

            user_input = str(input_data["user_input"])
            logger.info(f"Processing preferences for user input: {user_input[:100]}...")

            # Check if in demo mode
            if self.config.demo_mode or self.api_client is None:
                logger.info("Using mock data for preferences (demo mode)")
                preferences = get_mock_preferences(user_input)
                response_text = json.dumps(preferences, indent=2)
            else:
                prompt = self._create_prompt(self.system_prompt, user_input)

                # Generate response
                response_text = self.api_client.generate_content(
                    prompt, temperature=0.3  # Lower temperature for more consistent extraction
                )

                # Parse JSON response
                preferences = self._parse_json_response(response_text)

            logger.info(f"Successfully extracted preferences: {list(preferences.keys())}")
            return {
                "success": True,
                "preferences": preferences,
                "raw_response": response_text,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}", exc_info=True)
            # Fallback: return structured response with raw text
            return {
                "success": False,
                "preferences": self._create_fallback_preferences(response_text),
                "raw_response": response_text,
                "error": "Failed to parse structured response",
            }

        except Exception as e:
            logger.error(f"Error processing preferences: {e}", exc_info=True)
            raise RuntimeError(f"Failed to extract preferences: {e}") from e

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response from API.

        Args:
            response_text: Raw response text that should contain JSON.

        Returns:
            Parsed preferences dictionary.
        """
        # Try to extract JSON from response (might have markdown code blocks)
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        # Parse JSON
        return json.loads(text)

    def _create_fallback_preferences(self, raw_text: str) -> Dict[str, Any]:
        """
        Create fallback preferences structure when JSON parsing fails.

        Args:
            raw_text: Raw response text.

        Returns:
            Basic preferences structure.
        """
        return {
            "interests": [],
            "travel_style": None,
            "accommodation_type": None,
            "dietary_restrictions": [],
            "special_requirements": [],
            "additional_notes": raw_text,
        }

