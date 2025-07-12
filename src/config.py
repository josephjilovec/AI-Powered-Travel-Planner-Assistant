# src/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This should be called at the very beginning of your application's startup.
load_dotenv()

# --- General Application Settings ---
APP_NAME = "AI-Powered Travel Planner Assistant"
APP_VERSION = "1.0.0"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() # Default to INFO, can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# --- Gemini API Settings ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = "gemini-2.0-flash" # The specific Gemini model to use

# --- Agent Personas and Descriptions ---
# These define the roles and prompt guidance for each AI agent.
AGENT_PERSONAS = {
    "preference_agent": {
        "id_prefix": "PrefAgent",
        "persona": "User Preference Analyst",
        "description": "Understands and extracts user's travel desires and constraints.",
        "prompt_guidance": "You are a user preference analyst. Carefully extract all travel preferences, constraints, and desires from the user's input. Be thorough and ask clarifying questions if needed to build a complete profile."
    },
    "flight_search_agent": {
        "id_prefix": "FlightAgent",
        "persona": "Global Flight Finder",
        "description": "Searches for optimal flight options based on preferences.",
        "prompt_guidance": "You are a global flight finder. Based on the provided preferences, identify suitable flight options. Consider dates, budget, and destinations. If external tools were available, you would use them here."
    },
    "accommodation_search_agent": {
        "id_prefix": "AccomAgent",
        "persona": "Accommodation Curator",
        "description": "Finds suitable hotels, resorts, or other lodging options.",
        "prompt_guidance": "You are an accommodation curator. Find suitable lodging options (hotels, resorts, etc.) based on the user's destination, budget, and style preferences. If external tools were available, you would use them here."
    },
    "activity_search_agent": {
        "id_prefix": "ActivityAgent",
        "persona": "Experience Planner",
        "description": "Suggests activities, tours, and attractions for the destination.",
        "prompt_guidance": "You are an experience planner. Suggest engaging activities, tours, and attractions tailored to the user's interests and destination. Consider duration and type of activity. If external tools were available, you would use them here."
    },
    "itinerary_agent": {
        "id_prefix": "ItinAgent",
        "persona": "Itinerary Architect",
        "description": "Constructs a detailed, day-by-day travel itinerary.",
        "prompt_guidance": "You are an itinerary architect. Create a logical, detailed, day-by-day travel itinerary based on all collected information (preferences, flights, accommodations, activities). Ensure feasibility and flow."
    },
    "booking_support_agent": {
        "id_prefix": "BookAgent",
        "persona": "Travel Concierge",
        "description": "Provides simulated booking assistance and ongoing trip support.",
        "prompt_guidance": "You are a travel concierge. Provide clear, actionable steps for booking (simulated) and offer ongoing support for the trip. Emphasize that actual booking is simulated."
    }
}

# --- Simulated External Integration Settings ---
# These are used by agents to simulate calls to external APIs
SIMULATED_FLIGHT_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mock_flights.json')
SIMULATED_ACCOMMODATION_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mock_accommodations.json')
SIMULATED_ACTIVITY_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mock_activities.json')

# --- Validation and Warnings ---
if GEMINI_API_KEY is None:
    print("WARNING: GEMINI_API_KEY is not set in environment variables. AI functionalities may not work.")
    print("Please create a .env file in the project root with GEMINI_API_KEY=YOUR_KEY_HERE")

# Example of how to access configurations
if __name__ == "__main__":
    print(f"Application Name: {APP_NAME}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Gemini Model: {GEMINI_MODEL_NAME}")
    print(f"Gemini API Key (first 5 chars): {GEMINI_API_KEY[:5] if GEMINI_API_KEY else 'N/A'}")
    print(f"Preference Agent Persona: {AGENT_PERSONAS['preference_agent']['persona']}")
    print(f"Simulated Flight Data Path: {SIMULATED_FLIGHT_DATA_PATH}")
