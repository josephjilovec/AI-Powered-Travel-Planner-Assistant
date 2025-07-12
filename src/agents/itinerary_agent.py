# src/agents/itinerary_agent.py

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent
from src.agents.gemini_service import GeminiService
from src.config import AGENT_PERSONAS # Import agent personas from config

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ItineraryAgent(BaseAgent):
    """
    The ItineraryAgent is a specialized AI agent responsible for constructing
    a detailed, day-by-day travel itinerary. It takes user preferences and
    recommended travel components (flights, hotels, activities) as input,
    and leverages the Google Gemini API to create a personalized plan,
    ensuring logical flow and handling temporal dependencies.
    """

    def __init__(self, agent_id: str, gemini_service: GeminiService):
        """
        Initializes the ItineraryAgent.

        Args:
            agent_id (str): A unique identifier for this agent instance.
            gemini_service (GeminiService): An instance of the GeminiService for API interactions.
        """
        persona_info = AGENT_PERSONAS.get("itinerary_agent", {})
        super().__init__(
            agent_id=agent_id,
            persona=persona_info.get("persona", "Default Itinerary Architect"),
            description=persona_info.get("description", "Constructs detailed daily travel plans.")
        )
        self.gemini_service = gemini_service
        self.chat_history: List[Dict[str, Any]] = [] # Stores conversational context for Gemini
        logger.info(f"ItineraryAgent '{self.agent_id}' initialized.")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes travel components and user preferences to generate a day-by-day itinerary.

        The `task_data` dictionary is expected to contain:
        - 'preferences': A dictionary of extracted user preferences.
        - 'recommendations': A dictionary containing lists of recommended flights, hotels, and activities.
                             (e.g., from SearchRecommendationAgent)

        Args:
            task_data (Dict[str, Any]): A dictionary containing all necessary data for itinerary creation.

        Returns:
            Dict[str, Any]: A dictionary containing the generated itinerary:
                            - 'status': "success" or "failed".
                            - 'itinerary': A structured list of daily plans.
                            - 'agent_id': The ID of this agent.
                            - 'error': (Optional) Error message if operation failed.
        """
        preferences = task_data.get('preferences')
        recommendations = task_data.get('recommendations')

        if not preferences or not recommendations:
            logger.error(f"[{self.agent_id}] Missing preferences or recommendations for itinerary generation.")
            return {
                "status": "failed",
                "itinerary": [],
                "agent_id": self.agent_id,
                "error": "Missing essential data for itinerary creation."
            }

        logger.info(f"[{self.agent_id}] Generating itinerary based on preferences and recommendations.")

        # Extract key information for the prompt
        destination = preferences.get('destination', 'the chosen destination')
        start_date_str = preferences.get('start_date')
        end_date_str = preferences.get('end_date')
        interests = preferences.get('interests', [])
        travel_style = preferences.get('travel_style', 'flexible')

        if not start_date_str or not end_date_str:
            logger.error(f"[{self.agent_id}] Start and end dates are required for itinerary generation.")
            return {
                "status": "failed",
                "itinerary": [],
                "agent_id": self.agent_id,
                "error": "Start and end dates are required to create an itinerary."
            }

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date.")
        except ValueError as e:
            logger.error(f"[{self.agent_id}] Invalid date format or logic: {e}")
            return {
                "status": "failed",
                "itinerary": [],
                "agent_id": self.agent_id,
                "error": f"Invalid date format or range: {e}"
            }

        # Prepare data for Gemini
        recommended_flights = recommendations.get('recommended_flights', [])
        recommended_hotels = recommendations.get('recommended_hotels', [])
        recommended_activities = recommendations.get('recommended_activities', [])

        # Construct the prompt for Gemini
        prompt_guidance = AGENT_PERSONAS["itinerary_agent"]["prompt_guidance"]
        itinerary_prompt = f"""
        {prompt_guidance}

        Create a detailed, day-by-day travel itinerary for a trip to {destination}.

        **Trip Details:**
        -   Start Date: {start_date_str}
        -   End Date: {end_date_str}
        -   Interests: {', '.join(interests) if interests else 'Not specified'}
        -   Travel Style: {travel_style}

        **Recommended Travel Components:**
        -   Flights: {json.dumps(recommended_flights, indent=2)}
        -   Hotels: {json.dumps(recommended_hotels, indent=2)}
        -   Activities: {json.dumps(recommended_activities, indent=2)}

        **Guidelines for Itinerary Creation:**
        1.  **Logical Flow**: Ensure activities are logically grouped by location or time.
        2.  **Dependencies**: Account for flight arrival/departure times. On arrival day, suggest activities after check-in. On departure day, suggest activities before check-out and flight.
        3.  **Hotel Integration**: Assume the user will stay at one of the recommended hotels for the duration.
        4.  **Interests**: Prioritize activities aligning with user interests.
        5.  **Balance**: Mix sightseeing, relaxation, and food experiences.
        6.  **Flexibility**: Keep the '{travel_style}' style in mind (e.g., less packed for 'relaxed').
        7.  **Format**: Return the itinerary as a JSON array where each element represents a day.

        **JSON Schema for Itinerary:**
        ```json
        [
            {{
                "date": "YYYY-MM-DD",
                "day_of_week": "Monday",
                "theme": "Arrival and City Exploration",
                "events": [
                    {{
                        "time": "HH:MM",
                        "description": "Event description (e.g., 'Arrive at JFK Airport', 'Check into hotel', 'Visit Louvre Museum')",
                        "details": {{}} // Optional: include relevant flight/hotel/activity details here
                    }}
                ]
            }}
        ]
        ```
        Ensure the 'details' object within 'events' is populated with relevant data from the recommended components if an event directly relates to them (e.g., flight number, hotel name, activity ID).
        """

        # Define the JSON schema for the expected itinerary output
        itinerary_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "date": {"type": "STRING", "format": "date"},
                    "day_of_week": {"type": "STRING"},
                    "theme": {"type": "STRING"},
                    "events": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "time": {"type": "STRING"},
                                "description": {"type": "STRING"},
                                "details": {"type": "OBJECT"} # Flexible object for nested details
                            },
                            "required": ["time", "description"]
                        }
                    }
                },
                "required": ["date", "day_of_week", "theme", "events"]
            }
        }

        try:
            gemini_response_text = await self.gemini_service.call_gemini_api(
                self.chat_history,
                itinerary_prompt,
                response_schema=itinerary_schema
            )

            self.chat_history.append({"role": "user", "parts": [{"text": itinerary_prompt}]})
            self.chat_history.append({"role": "model", "parts": [{"text": gemini_response_text}]})

            generated_itinerary = json.loads(gemini_response_text)
            if not isinstance(generated_itinerary, list):
                raise ValueError("Gemini response is not a JSON array for itinerary.")

            logger.info(f"[{self.agent_id}] Successfully generated itinerary with {len(generated_itinerary)} days.")

            return {
                "status": "success",
                "itinerary": generated_itinerary,
                "agent_id": self.agent_id
            }

        except json.JSONDecodeError as e:
            logger.error(f"[{self.agent_id}] Failed to parse JSON response from Gemini for itinerary: {e}. Raw response: {gemini_response_text[:500]}...")
            return {
                "status": "failed",
                "itinerary": [],
                "agent_id": self.agent_id,
                "error": f"JSON parsing error for itinerary: {e}"
            }
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error during itinerary generation: {e}", exc_info=True)
            return {
                "status": "failed",
                "itinerary": [],
                "agent_id": self.agent_id,
                "error": str(e)
            }

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the ItineraryAgent.
    Requires a mock or real GeminiService.
    """
    # Mock GeminiService for local testing without actual API calls
    class MockGeminiService:
        async def call_gemini_api(self, chat_history: List[Dict[str, Any]], prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
            # Simulate a response that structures an itinerary
            if "Create a detailed, day-by-day travel itinerary" in prompt:
                return json.dumps([
                    {
                        "date": "2024-09-10",
                        "day_of_week": "Tuesday",
                        "theme": "Arrival and Eiffel Tower Charm",
                        "events": [
                            {"time": "14:00", "description": "Arrive at Paris CDG Airport", "details": {"flight_id": "FL003"}},
                            {"time": "16:00", "description": "Check into The Parisian Grand Hotel", "details": {"hotel_name": "The Parisian Grand"}},
                            {"time": "18:00", "description": "Eiffel Tower Summit Experience", "details": {"activity_name": "Eiffel Tower Summit Experience", "price": 60.00}},
                            {"time": "20:00", "description": "Dinner near Eiffel Tower"}
                        ]
                    },
                    {
                        "date": "2024-09-11",
                        "day_of_week": "Wednesday",
                        "theme": "Art and Culture Immersion",
                        "events": [
                            {"time": "09:00", "description": "Visit Louvre Museum", "details": {"activity_name": "Louvre Museum Visit", "price": 20.00}},
                            {"time": "13:00", "description": "Lunch at a traditional French bistro"},
                            {"time": "15:00", "description": "Stroll through Tuileries Garden"},
                            {"time": "19:00", "description": "Seine River Cruise", "details": {"activity_name": "Paris Seine River Cruise", "price": 30.00}}
                        ]
                    },
                    {
                        "date": "2024-09-15",
                        "day_of_week": "Sunday",
                        "theme": "Departure Day",
                        "events": [
                            {"time": "09:00", "description": "Enjoy breakfast at hotel"},
                            {"time": "11:00", "description": "Check out from The Parisian Grand Hotel", "details": {"hotel_name": "The Parisian Grand"}},
                            {"time": "13:00", "description": "Depart from Paris CDG Airport", "details": {"flight_id": "FL004"}}
                        ]
                    }
                ])
            return json.dumps([]) # Default empty itinerary

    # Create an instance of the mock Gemini service
    mock_gemini_service = MockGeminiService()

    # Create the ItineraryAgent
    itinerary_agent = ItineraryAgent("ItinAgent-001", mock_gemini_service)

    # --- Test Case: Full trip planning data ---
    sample_preferences = {
        "destination": "Paris",
        "start_date": "2024-09-10",
        "end_date": "2024-09-15",
        "budget_per_person": 2000.00,
        "interests": ["art", "culture", "food", "sightseeing"],
        "travel_style": "romantic",
        "number_of_travelers": 2
    }

    sample_recommendations = {
        "recommended_flights": [
            {"flight_id": "FL003", "origin": "LAX", "destination": "CDG", "departure_date": "2024-09-10", "departure_time": "14:00", "price": 750.00},
            {"flight_id": "FL004", "origin": "CDG", "destination": "LAX", "departure_date": "2024-09-15", "departure_time": "13:00", "price": 700.00}
        ],
        "recommended_hotels": [
            {"hotel_id": "H001", "name": "The Parisian Grand"
