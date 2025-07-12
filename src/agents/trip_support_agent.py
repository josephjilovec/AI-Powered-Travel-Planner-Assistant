# src/agents/trip_support_agent.py

import json
import logging
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent
from src.agents.gemini_service import GeminiService
from src.config import AGENT_PERSONAS # Import agent personas from config

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TripSupportAgent(BaseAgent):
    """
    The TripSupportAgent is a specialized AI agent that provides ongoing trip support
    to the user. It answers real-time questions about their itinerary, bookings,
    and destination, and can provide (simulated) rebooking assistance or escalation pathways.
    It leverages the Google Gemini API for conversational understanding and response generation.
    """

    def __init__(self, agent_id: str, gemini_service: GeminiService):
        """
        Initializes the TripSupportAgent.

        Args:
            agent_id (str): A unique identifier for this agent instance.
            gemini_service (GeminiService): An instance of the GeminiService for API interactions.
        """
        persona_info = AGENT_PERSONAS.get("booking_support_agent", {}) # Using booking support persona
        super().__init__(
            agent_id=agent_id,
            persona=persona_info.get("persona", "Default Travel Concierge"),
            description=persona_info.get("description", "Provides ongoing trip support and booking assistance.")
        )
        self.gemini_service = gemini_service
        self.chat_history: List[Dict[str, Any]] = [] # Stores conversational context for Gemini
        logger.info(f"TripSupportAgent '{self.agent_id}' initialized.")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a user's real-time query for trip support.

        The `task_data` dictionary is expected to contain:
        - 'user_query': The user's question or request.
        - 'trip_context': A dictionary containing relevant information about the trip, e.g.:
                          - 'current_itinerary': (Optional) The full itinerary.
                          - 'confirmed_bookings': (Optional) A list of confirmed booking details.
                          - 'user_preferences': (Optional) Original user preferences.

        Args:
            task_data (Dict[str, Any]): A dictionary containing the user's query and trip context.

        Returns:
            Dict[str, Any]: A dictionary containing the agent's response:
                            - 'status': "success" or "failed".
                            - 'response_text': The conversational response to the user.
                            - 'agent_id': The ID of this agent.
                            - 'action_suggested': (Optional) e.g., "rebooking", "escalate_to_human", "information_provided"
                            - 'error': (Optional) Error message if operation failed.
        """
        user_query = task_data.get('user_query')
        trip_context = task_data.get('trip_context', {})

        if not user_query:
            logger.error(f"[{self.agent_id}] No user query provided for trip support.")
            return {
                "status": "failed",
                "response_text": "Please provide a query for trip support.",
                "agent_id": self.agent_id,
                "action_suggested": "none",
                "error": "Missing user query."
            }

        logger.info(f"[{self.agent_id}] Processing trip support query: '{user_query}'")

        # Prepare the context for Gemini
        context_str = "No specific trip context provided."
        if trip_context:
            context_str = json.dumps(trip_context, indent=2)

        # Construct the prompt for Gemini
        prompt_guidance = AGENT_PERSONAS["booking_support_agent"]["prompt_guidance"]
        support_prompt = f"""
        {prompt_guidance}

        The user has a question or request regarding their trip. Provide a helpful and concise response.
        If the request implies a booking change or a complex issue, suggest a simulated action
        like "initiating rebooking process" or "escalating to human support" and explain that this is simulated.

        User Query: "{user_query}"

        Current Trip Context (if available):
        ---
        {context_str}
        ---

        Your response should directly address the user's query. If you suggest a simulated action,
        make it clear that it's a simulation.
        """

        try:
            gemini_response_text = await self.gemini_service.call_gemini_api(
                self.chat_history,
                support_prompt
            )

            # Update chat history
            self.chat_history.append({"role": "user", "parts": [{"text": support_prompt}]})
            self.chat_history.append({"role": "model", "parts": [{"text": gemini_response_text}]})

            # Simple logic to determine action suggested based on keywords
            action_suggested = "information_provided"
            if "rebooking" in gemini_response_text.lower() or "change my booking" in user_query.lower():
                action_suggested = "simulated_rebooking"
            elif "contact support" in gemini_response_text.lower() or "escalate" in gemini_response_text.lower():
                action_suggested = "simulated_escalation_to_human"
            elif "cancel" in gemini_response_text.lower() or "cancel my trip" in user_query.lower():
                action_suggested = "simulated_cancellation"


            logger.info(f"[{self.agent_id}] Generated support response. Action suggested: {action_suggested}")

            return {
                "status": "success",
                "response_text": gemini_response_text,
                "agent_id": self.agent_id,
                "action_suggested": action_suggested
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Error during trip support response generation: {e}", exc_info=True)
            return {
                "status": "failed",
                "response_text": "I apologize, but I encountered an error trying to process your request. Please try again later.",
                "agent_id": self.agent_id,
                "action_suggested": "error",
                "error": str(e)
            }

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the TripSupportAgent.
    Requires a mock or real GeminiService.
    """
    # Mock GeminiService for local testing without actual API calls
    class MockGeminiService:
        async def call_gemini_api(self, chat_history: List[Dict[str, Any]], prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
            if "flight number for tomorrow" in prompt:
                return "Your flight number for tomorrow is FL001, departing at 08:00 AM. Please arrive at the airport 2 hours before departure."
            elif "hotel located" in prompt:
                return "Your hotel, The Parisian Grand, is located at 123 Rue de la Paix, Paris. It's very central!"
            elif "change my activity booking" in prompt:
                return "I can help you with that! This is a simulated rebooking process. Please confirm which activity you'd like to change and your preferred new date/time."
            elif "weather like in Paris" in prompt:
                return "The weather in Paris next week is expected to be partly cloudy with temperatures around 20°C (68°F). Perfect for sightseeing!"
            elif "cancel my trip" in prompt:
                return "I understand you wish to cancel your trip. This is a simulated cancellation. Please note that cancellation policies may apply. Are you sure you want to proceed?"
            return "I'm sorry, I couldn't find specific information for that. Can you please rephrase your question?"

    # Create an instance of the mock Gemini service
    mock_gemini_service = MockGeminiService()

    # Create the TripSupportAgent
    support_agent = TripSupportAgent("SupportAgent-001", mock_gemini_service)

    # Sample trip context (would come from previous agent outputs or persistent storage)
    sample_itinerary = [
        {"date": "2024-09-10", "events": [{"time": "14:00", "description": "Arrive at Paris CDG Airport", "details": {"flight_id": "FL001"}}]},
        {"date": "2024-09-11", "events": [{"time": "09:00", "description": "Visit Louvre Museum"}]}
    ]
    sample_bookings = [
        {"type": "flight", "id": "FL001", "details": {"flight_number": "AA123", "date": "2024-09-10"}},
        {"type": "hotel", "id": "H001", "details": {"name": "The Parisian Grand", "address": "123 Rue de la Paix"}}
    ]
    sample_preferences = {"destination": "Paris", "start_date": "2024-09-10"}

    trip_context_data = {
        "current_itinerary": sample_itinerary,
        "confirmed_bookings": sample_bookings,
        "user_preferences": sample_preferences
    }

    # --- Test Cases ---

    print("\n--- Test Case 1: Query about flight number ---")
    query1_data = {"user_query": "What's my flight number for tomorrow?", "trip_context": trip_context_data}
    result1 = await support_agent.process_task(query1_data)
    print(f"Result 1: {json.dumps(result1, indent=2)}")

    print("\n--- Test Case 2: Query about hotel location ---")
    query2_data = {"user_query": "Where is my hotel located?", "trip_context": trip_context_data}
    result2 = await support_agent.process_task(query2_data)
    print(f"Result 2: {json.dumps(result2, indent=2)}")

    print("\n--- Test Case 3: Request to change booking (simulated) ---")
    query3_data = {"user_query": "Can I change my activity booking for the Louvre?", "trip_context": trip_context_data}
    result3 = await support_agent.process_task(query3_data)
    print(f"Result 3: {json.dumps(result3, indent=2)}")

    print("\n--- Test Case 4: General question (weather) ---")
    query4_data = {"user_query": "What's the weather like in Paris next week?", "trip_context": trip_context_data}
    result4 = await support_agent.process_task(query4_data)
    print(f"Result 4: {json.dumps(result4, indent=2)}")

    print("\n--- Test Case 5: Request to cancel trip (simulated) ---")
    query5_data = {"user_query": "I need to cancel my trip, please.", "trip_context": trip_context_data}
    result5 = await support_agent.process_task(query5_data)
    print(f"Result 5: {json.dumps(result5, indent=2)}")

    print("\n--- Test Case 6: Unclear query ---")
    query6_data = {"user_query": "Tell me something.", "trip_context": trip_context_data}
    result6 = await support_agent.process_task(query6_data)
    print(f"Result 6: {json.dumps(result6, indent=2)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
