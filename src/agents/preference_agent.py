# src/agents/preference_agent.py

import json
import logging
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent
from src.agents.gemini_service import GeminiService
from src.config import AGENT_PERSONAS # Import agent personas from config

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreferenceAgent(BaseAgent):
    """
    The PreferenceAgent is a specialized AI agent responsible for conversing with the user
    to gather and extract their travel preferences. It uses the Google Gemini API
    to understand natural language input and structure it into a usable format
    including budget, destination, dates, interests, and travel style.
    """

    def __init__(self, agent_id: str, gemini_service: GeminiService):
        """
        Initializes the PreferenceAgent.

        Args:
            agent_id (str): A unique identifier for this agent instance.
            gemini_service (GeminiService): An instance of the GeminiService for API interactions.
        """
        persona_info = AGENT_PERSONAS.get("preference_agent", {})
        super().__init__(
            agent_id=agent_id,
            persona=persona_info.get("persona", "Default Preference Analyst"),
            description=persona_info.get("description", "Gathers user travel preferences.")
        )
        self.gemini_service = gemini_service
        self.chat_history: List[Dict[str, Any]] = [] # Stores conversational context
        logger.info(f"PreferenceAgent '{self.agent_id}' initialized.")

    async def process_task(self, user_query: str) -> Dict[str, Any]:
        """
        Processes a user's natural language query to extract travel preferences.

        Args:
            user_query (str): The user's input describing their travel desires.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted preferences.
                            Keys include: 'destination', 'start_date', 'end_date',
                            'budget_per_person', 'interests', 'travel_style', 'number_of_travelers'.
                            Values will be None if not found or extracted.
                            Also includes 'status' and 'agent_id'.
        """
        logger.info(f"[{self.agent_id}] Processing user query for preferences: '{user_query}'")

        # Define the JSON schema for the expected output from Gemini
        # This helps Gemini return structured data reliably.
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "destination": {"type": "STRING", "description": "Desired travel destination (e.g., 'Paris', 'Cancun')."},
                "start_date": {"type": "STRING", "format": "date", "description": "Planned start date of the trip (YYYY-MM-DD)."},
                "end_date": {"type": "STRING", "format": "date", "description": "Planned end date of the trip (YYYY-MM-DD)."},
                "budget_per_person": {"type": "NUMBER", "description": "Approximate budget per person for the trip, in USD."},
                "interests": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of user's interests (e.g., 'history', 'beach', 'adventure', 'food', 'art')."
                },
                "travel_style": {"type": "STRING", "description": "Preferred travel style (e.g., 'luxury', 'budget', 'family-friendly', 'solo adventure', 'romantic')."},
                "number_of_travelers": {"type": "NUMBER", "description": "Total number of people traveling."}
            },
            "required": [] # None are strictly required, as user might provide partial info
        }

        # Construct the prompt for Gemini
        prompt_guidance = AGENT_PERSONAS["preference_agent"]["prompt_guidance"]
        prompt = f"""
        {prompt_guidance}

        Extract the following travel preferences from the user's query. If a piece of information
        is not explicitly mentioned, omit it from the JSON.

        User Query: "{user_query}"

        Return the extracted preferences as a JSON object, strictly following this schema:
        {json.dumps(response_schema, indent=2)}
        """

        try:
            gemini_response_text = await self.gemini_service.call_gemini_api(
                self.chat_history,
                prompt,
                response_schema=response_schema
            )

            # Update chat history for potential future turns (e.g., clarifying questions)
            self.chat_history.append({"role": "user", "parts": [{"text": prompt}]})
            self.chat_history.append({"role": "model", "parts": [{"text": gemini_response_text}]})

            # Gemini should return pure JSON due to response_schema, but we'll try to parse
            extracted_preferences = json.loads(gemini_response_text)

            logger.info(f"[{self.agent_id}] Successfully extracted preferences: {extracted_preferences}")
            return {
                "status": "success",
                "preferences": extracted_preferences,
                "agent_id": self.agent_id
            }

        except json.JSONDecodeError as e:
            logger.error(f"[{self.agent_id}] Failed to parse JSON response from Gemini: {e}. Raw response: {gemini_response_text[:500]}...")
            return {
                "status": "failed",
                "preferences": {},
                "agent_id": self.agent_id,
                "error": f"JSON parsing error: {e}"
            }
        except Exception as e:
            logger.error(f"[{self.agent_id}] Error during preference extraction: {e}", exc_info=True)
            return {
                "status": "failed",
                "preferences": {},
                "agent_id": self.agent_id,
                "error": str(e)
            }

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the PreferenceAgent.
    Requires a mock or real GeminiService.
    """
    # Mock GeminiService for local testing without actual API calls
    class MockGeminiService:
        async def call_gemini_api(self, chat_history: List[Dict[str, Any]], prompt: str, response_schema: Optional[Dict[str, Any]] = None) -> str:
            # Simulate different responses based on prompt content
            if "Paris" in prompt and "budget" in prompt:
                return json.dumps({
                    "destination": "Paris",
                    "start_date": "2024-10-01",
                    "end_date": "2024-10-07",
                    "budget_per_person": 2000.00,
                    "interests": ["art", "culture", "food"],
                    "travel_style": "romantic",
                    "number_of_travelers": 2
                })
            elif "beach" in prompt and "Cancun" in prompt:
                return json.dumps({
                    "destination": "Cancun",
                    "start_date": "2025-03-15",
                    "end_date": "2025-03-22",
                    "interests": ["beach", "adventure", "relaxation"],
                    "travel_style": "family-friendly",
                    "number_of_travelers": 4
                })
            elif "solo trip" in prompt:
                return json.dumps({
                    "destination": "Kyoto",
                    "travel_style": "solo adventure",
                    "interests": ["history", "nature"]
                })
            return json.dumps({}) # Default empty response

    # Create an instance of the mock Gemini service
    mock_gemini_service = MockGeminiService()

    # Create the PreferenceAgent
    pref_agent = PreferenceAgent("PrefAgent-001", mock_gemini_service)

    # --- Test Cases ---

    print("\n--- Test Case 1: Detailed Paris Trip ---")
    query1 = "I want to go to Paris for a romantic trip from October 1st to 7th, 2024. My budget is around $2000 per person, and I'm interested in art, culture, and food. There will be two of us."
    result1 = await pref_agent.process_task(query1)
    print(f"Result 1: {json.dumps(result1, indent=2)}")

    print("\n--- Test Case 2: Family Beach Vacation in Cancun ---")
    query2 = "We are a family of four looking for a beach adventure in Cancun next spring break, around mid-March 2025. We love relaxation and some adventure activities."
    result2 = await pref_agent.process_task(query2)
    print(f"Result 2: {json.dumps(result2, indent=2)}")

    print("\n--- Test Case 3: Solo Trip, partial info ---")
    query3 = "I'm planning a solo trip, maybe to Kyoto. I like history and nature."
    result3 = await pref_agent.process_task(query3)
    print(f"Result 3: {json.dumps(result3, indent=2)}")

    print("\n--- Test Case 4: Ambiguous/Minimal info ---")
    query4 = "I want to travel somewhere nice."
    result4 = await pref_agent.process_task(query4)
    print(f"Result 4: {json.dumps(result4, indent=2)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
