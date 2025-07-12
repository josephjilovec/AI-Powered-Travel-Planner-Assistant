# src/agents/search_recommendation_agent.py

import json
import logging
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent
from src.agents.gemini_service import GeminiService
from src.agents.tools.flight_search_tool import FlightSearchTool
from src.agents.tools.hotel_search_tool import HotelSearchTool
from src.agents.tools.activity_search_tool import ActivitySearchTool
from src.config import AGENT_PERSONAS # Import agent personas from config

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchRecommendationAgent(BaseAgent):
    """
    The SearchRecommendationAgent is a specialized AI agent that interprets user preferences,
    calls simulated external travel tools (Flight, Hotel, Activity search),
    filters and ranks the results, and generates tailored recommendations.
    It leverages the Google Gemini API for intelligent interpretation and recommendation generation.
    """

    def __init__(self, agent_id: str, gemini_service: GeminiService):
        """
        Initializes the SearchRecommendationAgent with necessary tools and services.

        Args:
            agent_id (str): A unique identifier for this agent instance.
            gemini_service (GeminiService): An instance of the GeminiService for API interactions.
        """
        persona_info = AGENT_PERSONAS.get("flight_search_agent", {}) # Using flight search persona as a general search persona
        super().__init__(
            agent_id=agent_id,
            persona=persona_info.get("persona", "Default Search Recommender"),
            description=persona_info.get("description", "Searches and recommends travel options.")
        )
        self.gemini_service = gemini_service
        self.flight_search_tool = FlightSearchTool()
        self.hotel_search_tool = HotelSearchTool()
        self.activity_search_tool = ActivitySearchTool()
        self.chat_history: List[Dict[str, Any]] = [] # Stores conversational context
        logger.info(f"SearchRecommendationAgent '{self.agent_id}' initialized with travel tools.")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes user preferences to search for and recommend travel options.

        The `task_data` dictionary is expected to contain:
        - 'preferences': A dictionary of extracted user preferences (from PreferenceAgent).
                         Expected keys: 'destination', 'start_date', 'end_date',
                         'budget_per_person', 'interests', 'travel_style', 'number_of_travelers'.

        Args:
            task_data (Dict[str, Any]): A dictionary containing user preferences.

        Returns:
            Dict[str, Any]: A dictionary containing the search recommendations:
                            - 'status': "success" or "failed".
                            - 'recommendations': A structured dictionary of recommended flights, hotels, and activities.
                            - 'agent_id': The ID of this agent.
                            - 'error': (Optional) Error message if operation failed.
        """
        preferences = task_data.get('preferences')
        if not preferences:
            logger.error(f"[{self.agent_id}] No preferences provided for search recommendation.")
            return {
                "status": "failed",
                "recommendations": {},
                "agent_id": self.agent_id,
                "error": "Missing user preferences for search."
            }

        logger.info(f"[{self.agent_id}] Starting search recommendations for preferences: {preferences}")

        destination = preferences.get('destination')
        start_date = preferences.get('start_date')
        end_date = preferences.get('end_date')
        budget_per_person = preferences.get('budget_per_person')
        interests = preferences.get('interests', [])
        number_of_travelers = preferences.get('number_of_travelers', 1)

        if not destination or not start_date:
            logger.warning(f"[{self.agent_id}] Missing essential preferences (destination or start_date). Cannot proceed with full search.")
            return {
                "status": "failed",
                "recommendations": {},
                "agent_id": self.agent_id,
                "error": "Destination and start date are required for search."
            }

        all_flights = []
        all_hotels = []
        all_activities = []

        # --- Step 1: Search Flights ---
        flight_max_price = budget_per_person * number_of_travelers if budget_per_person else None
        try:
            # Assuming a fixed origin for simplicity in simulation, e.g., "LAX" or "Any"
            # In a real app, origin would also come from user preferences or current location.
            # For this example, let's assume a common departure hub or make it flexible.
            # We'll use a generic "Origin" and let the mock data filter.
            all_flights = await self.flight_search_tool.search_flights(
                origin="Any", # Placeholder for dynamic origin
                destination=destination,
                departure_date=start_date,
                return_date=end_date,
                passengers=number_of_travelers,
                max_price=flight_max_price,
                flexible_dates_days=2 # Allow some flexibility
            )
            logger.info(f"[{self.agent_id}] Flight search completed. Found {len(all_flights)} flights.")
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error searching flights: {e}")

        # --- Step 2: Search Hotels ---
        hotel_max_price_per_night = budget_per_person / 5 if budget_per_person else None # Arbitrary split for simulation
        try:
            all_hotels = await self.hotel_search_tool.search_hotels(
                destination=destination,
                check_in_date=start_date,
                check_out_date=end_date,
                guests=number_of_travelers,
                max_price_per_night=hotel_max_price_per_night,
                min_rating=preferences.get('min_hotel_rating'), # Example additional preference
                amenities=preferences.get('desired_amenities') # Example additional preference
            )
            logger.info(f"[{self.agent_id}] Hotel search completed. Found {len(all_hotels)} hotels.")
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error searching hotels: {e}")

        # --- Step 3: Search Activities ---
        activity_max_price = budget_per_person / 10 if budget_per_person else None # Arbitrary split
        try:
            all_activities = await self.activity_search_tool.search_activities(
                destination=destination,
                interests=interests,
                max_price=activity_max_price
            )
            logger.info(f"[{self.agent_id}] Activity search completed. Found {len(all_activities)} activities.")
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error searching activities: {e}")

        # --- Step 4: Use Gemini to filter and rank results ---
        # Provide Gemini with all collected data and ask it to select the best recommendations
        recommendation_prompt = f"""
        You are a travel recommendation expert. Based on the user's preferences and the available travel options,
        select the best 2-3 flights, 2-3 hotels, and 3-5 activities that best match the user's needs.
        If no suitable options are found for a category, return an empty list for that category.

        User Preferences:
        {json.dumps(preferences, indent=2)}

        Available Flights:
        {json.dumps(all_flights, indent=2)}

        Available Hotels:
        {json.dumps(all_hotels, indent=2)}

        Available Activities:
        {json.dumps(all_activities, indent=2)}

        Provide your recommendations as a JSON object with the following structure:
        {{
            "recommended_flights": [],
            "recommended_hotels": [],
            "recommended_activities": []
        }}
        Ensure each recommended item includes all its original details.
        Prioritize options that align with budget, dates, and interests.
        """

        recommendation_schema = {
            "type": "OBJECT",
            "properties": {
                "recommended_flights": {
                    "type": "ARRAY",
                    "items": {"type": "OBJECT"} # Flexible schema for flight details
                },
                "recommended_hotels": {
                    "type": "ARRAY",
                    "items": {"type": "OBJECT"} # Flexible schema for hotel details
                },
                "recommended_activities": {
                    "type": "ARRAY",
                    "items": {"type": "OBJECT"} # Flexible schema for activity details
                }
            },
            "required": ["recommended_flights", "recommended_hotels", "recommended_activities"]
        }

        try:
            gemini_response_text = await self.gemini_service.call_gemini_api(
                self.chat_history,
                recommendation_prompt,
                response_schema=recommendation_schema
            )

            self.chat_history.append({"role": "user", "parts": [{"text": recommendation_prompt}]})
            self.chat_history.append({"role": "model", "parts": [{"text": gemini_response_text}]})

            final_recommendations = json.loads(gemini_response_text)
            logger.info(f"[{self.agent_id}] Generated final recommendations.")

            return {
                "status": "success",
                "recommendations": final_recommendations,
                "agent_id": self.agent_id
            }

        except json.JSONDecodeError as e:
            logger.error(f"[{self.agent_id}] Failed to parse JSON response from Gemini for recommendations: {e}. Raw response: {gemini_response_text[:500]}...")
            return {
                "status": "failed",
                "recommendations": {},
                "agent_id": self.agent_id,
                "error": f"JSON parsing error for recommendations: {e}"
            }
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error during recommendation generation: {e}", exc_info=True)
            return {
                "status": "failed",
                "recommendations": {},
                "agent_id": self.agent_id,
                "error": str(e)
            }

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the SearchRecommendationAgent.
    Requires a mock or real GeminiService.
    """
    # Mock GeminiService for local testing without actual API calls
    class MockGeminiService:
        async def call_gemini_api(self, chat_history: List[Dict[str, Any]], prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
            # Simulate a response that structures recommendations
            if "User Preferences" in prompt:
                return json.dumps({
                    "recommended_flights": [
                        {"flight_id": "FL001", "origin": "LAX", "destination": "JFK", "departure_date": "2024-09-10", "price": 350.00}
                    ],
                    "recommended_hotels": [
                        {"hotel_id": "H004", "name": "New York City Loft", "destination": "New York", "price_per_night": 280.00}
                    ],
                    "recommended_activities": [
                        {"activity_id": "A004", "name": "Broadway Show Tickets", "destination": "New York", "price": 150.00},
                        {"activity_id": "A001", "name": "Eiffel Tower Summit Experience", "destination": "Paris", "price": 60.00} # Incorrect destination, but demonstrates selection
                    ]
                })
            return json.dumps({"recommended_flights": [], "recommended_hotels": [], "recommended_activities": []})

    # Create an instance of the mock Gemini service
    mock_gemini_service = MockGeminiService()

    # Create the SearchRecommendationAgent
    search_agent = SearchRecommendationAgent("SearchAgent-001", mock_gemini_service)

    # --- Test Case: User preferences for a trip ---
    sample_preferences = {
        "destination": "New York",
        "start_date": "2024-09-10",
        "end_date": "2024-09-15",
        "budget_per_person": 1000.00,
        "interests": ["art", "food", "theater"],
        "travel_style": "city break",
        "number_of_travelers": 2
    }

    search_task_data = {
        "preferences": sample_preferences
    }

    print("\n--- Running Search Recommendation Agent ---")
    recommendation_results = await search_agent.process_task(search_task_data)
    print(f"Recommendation Results: {json.dumps(recommendation_results, indent=2)}")

    print("\n--- Running Search Recommendation Agent with no destination ---")
    no_dest_preferences = {
        "start_date": "2024-09-10",
        "end_date": "2024-09-15",
        "budget_per_person": 1000.00,
        "interests": ["art"]
    }
    no_dest_results = await search_agent.process_task({"preferences": no_dest_preferences})
    print(f"No Destination Results: {json.dumps(no_dest_results, indent=2)}")


if __name__ == "__main__":
    import asyncio
    # Ensure mock data files exist for the tools to load
    from src.agents.tools.flight_search_tool import main as run_flight_tool_main
    from src.agents.tools.hotel_search_tool import main as run_hotel_tool_main
    from src.agents.tools.activity_search_tool import main as run_activity_tool_main
    
    # Run the main functions of the tools to create dummy data if they don't exist
    asyncio.run(run_flight_tool_main())
    asyncio.run(run_hotel_tool_main())
    asyncio.run(run_activity_tool_main())

    # Then run the agent's main
    asyncio.run(main())
