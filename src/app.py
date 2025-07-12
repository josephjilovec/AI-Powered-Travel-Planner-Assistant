# src/app.py

import os
import json
import logging
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # Import CORS for cross-origin requests

# Import core framework components
from src.agents.agent_manager import AgentManager
from src.agents.gemini_service import GeminiService
from src.config import AGENT_PERSONAS, LOG_LEVEL

# Import specialized AI agents
from src.agents.preference_agent import PreferenceAgent
from src.agents.search_recommendation_agent import SearchRecommendationAgent
from src.agents.itinerary_agent import ItineraryAgent
from src.agents.trip_support_agent import TripSupportAgent

# Configure logging for the Flask application
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
# Serve static files from the 'public' directory at the project root level
app = Flask(__name__, static_folder='../public')
CORS(app) # Enable CORS for all routes. In production, restrict this to your frontend's origin.

# Initialize core AI services and agent manager
gemini_service = GeminiService()
agent_manager = AgentManager()

# Initialize specialized AI agents
# Each agent gets a unique ID and the GeminiService instance
preference_agent = PreferenceAgent(f"{AGENT_PERSONAS['preference_agent']['id_prefix']}-001", gemini_service)
search_recommendation_agent = SearchRecommendationAgent(f"{AGENT_PERSONAS['flight_search_agent']['id_prefix']}-001", gemini_service)
itinerary_agent = ItineraryAgent(f"{AGENT_PERSONAS['itinerary_agent']['id_prefix']}-001", gemini_service)
trip_support_agent = TripSupportAgent(f"{AGENT_PERSONAS['booking_support_agent']['id_prefix']}-001", gemini_service)

# Register agents with the AgentManager
agent_manager.register_agent("preference_agent", preference_agent, "preference_collection")
agent_manager.register_agent("search_recommendation_agent", search_recommendation_agent, "search_recommendation")
agent_manager.register_agent("itinerary_agent", itinerary_agent, "itinerary_creation")
agent_manager.register_agent("trip_support_agent", trip_support_agent, "trip_support")

logger.info("All specialized AI agents initialized and registered with AgentManager.")

# --- Helper for running async functions in Flask routes ---
# Flask routes are typically synchronous. For async agent calls, we use asyncio.run().
# This is suitable for simple cases; for highly concurrent async Flask, an ASGI server
# (like uvicorn with Flask as an ASGI app) would be more performant.
def run_async(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

# --- API Endpoints ---

@app.route('/')
def serve_index():
    """Serves the main frontend HTML file."""
    logger.info("Serving index.html")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serves other static files (CSS, JS, images, etc.)."""
    logger.debug(f"Serving static file: {filename}")
    return send_from_directory(app.static_folder, filename)

@app.route('/plan_trip', methods=['POST'])
@run_async
async def plan_trip():
    """
    API endpoint to initiate a new travel plan.
    It orchestrates the sequence of AI agents: Preference -> Search -> Itinerary.
    """
    user_input = request.json.get('query')
    session_id = request.json.get('session_id', os.urandom(8).hex()) # Unique ID for the session

    if not user_input:
        logger.warning(f"[{session_id}] /plan_trip received empty query.")
        return jsonify({"status": "error", "message": "Please provide a query to plan your trip."}), 400

    logger.info(f"[{session_id}] Initiating trip planning for query: '{user_input[:50]}...'")

    try:
        # Step 1: Preference Gathering
        logger.info(f"[{session_id}] Dispatching task to Preference Agent.")
        preference_result = await agent_manager.dispatch_task(
            "preference_agent", {"user_query": user_input}
        )
        if preference_result.get("status") == "failed":
            logger.error(f"[{session_id}] Preference Agent failed: {preference_result.get('error')}")
            return jsonify({"status": "error", "message": "Could not understand your preferences. Please rephrase.", "details": preference_result.get("error")}), 500
        
        user_preferences = preference_result.get("preferences", {})
        if not user_preferences.get("destination"):
            logger.warning(f"[{session_id}] Preference Agent could not determine destination.")
            return jsonify({"status": "error", "message": "Please specify a destination for your trip."}), 400

        logger.info(f"[{session_id}] Preferences extracted: {user_preferences}")

        # Step 2: Search Recommendations (Flights, Hotels, Activities)
        logger.info(f"[{session_id}] Dispatching task to Search Recommendation Agent.")
        search_recommendation_result = await agent_manager.dispatch_task(
            "search_recommendation_agent", {"preferences": user_preferences}
        )
        if search_recommendation_result.get("status") == "failed":
            logger.error(f"[{session_id}] Search Recommendation Agent failed: {search_recommendation_result.get('error')}")
            return jsonify({"status": "error", "message": "Could not find suitable travel options. Please adjust preferences.", "details": search_recommendation_result.get("error")}), 500
        
        recommendations = search_recommendation_result.get("recommendations", {})
        logger.info(f"[{session_id}] Recommendations found: Flights={len(recommendations.get('recommended_flights', []))}, Hotels={len(recommendations.get('recommended_hotels', []))}, Activities={len(recommendations.get('recommended_activities', []))}")

        # Step 3: Itinerary Creation
        logger.info(f"[{session_id}] Dispatching task to Itinerary Agent.")
        itinerary_task_data = {
            "preferences": user_preferences,
            "recommendations": recommendations
        }
        itinerary_result = await agent_manager.dispatch_task(
            "itinerary_agent", itinerary_task_data
        )
        if itinerary_result.get("status") == "failed":
            logger.error(f"[{session_id}] Itinerary Agent failed: {itinerary_result.get('error')}")
            return jsonify({"status": "error", "message": "Could not generate an itinerary. Please check dates/destination.", "details": itinerary_result.get("error")}), 500
        
        itinerary = itinerary_result.get("itinerary", [])
        logger.info(f"[{session_id}] Itinerary created with {len(itinerary)} days.")

        # Combine all results for the frontend
        full_trip_plan = {
            "preferences": user_preferences,
            "recommendations": recommendations,
            "itinerary": itinerary
        }

        logger.info(f"[{session_id}] Trip planning completed successfully.")
        return jsonify({"status": "success", "message": "Trip plan generated!", "data": full_trip_plan}), 200

    except ValueError as e:
        logger.error(f"[{session_id}] API/Configuration error: {e}")
        return jsonify({"status": "error", "message": f"Server configuration or data error: {e}"}), 500
    except Exception as e:
        logger.exception(f"[{session_id}] An unexpected error occurred during trip planning orchestration: {e}")
        return jsonify({"status": "error", "message": f"An internal server error occurred: {e}"}), 500

@app.route('/chat', methods=['POST'])
@run_async
async def chat_with_assistant():
    """
    API endpoint for ongoing conversational trip support.
    Interacts with the TripSupportAgent.
    """
    user_message = request.json.get('message')
    # This 'trip_context' would ideally be retrieved from a session/database
    # but for simplicity, we assume frontend sends it or it's empty for new chats.
    trip_context = request.json.get('trip_context', {})
    session_id = request.json.get('session_id', os.urandom(8).hex())

    if not user_message:
        logger.warning(f"[{session_id}] /chat received empty message.")
        return jsonify({"status": "error", "message": "Please provide a message for the assistant."}), 400

    logger.info(f"[{session_id}] Chat message received: '{user_message[:50]}...'")

    try:
        support_task_data = {
            "user_query": user_message,
            "trip_context": trip_context
        }
        support_result = await agent_manager.dispatch_task(
            "trip_support_agent", support_task_data
        )

        if support_result.get("status") == "failed":
            logger.error(f"[{session_id}] Trip Support Agent failed: {support_result.get('error')}")
            return jsonify({"status": "error", "message": "I'm having trouble with that request. Please try again.", "details": support_result.get("error")}), 500
        
        response_text = support_result.get("response_text", "I'm sorry, I couldn't generate a response.")
        action_suggested = support_result.get("action_suggested", "none")

        logger.info(f"[{session_id}] Chat response generated. Action: {action_suggested}")
        return jsonify({
            "status": "success",
            "response": response_text,
            "action_suggested": action_suggested,
            "session_id": session_id # Return session ID for continuity
        }), 200

    except ValueError as e:
        logger.error(f"[{session_id}] API/Configuration error in chat: {e}")
        return jsonify({"status": "error", "message": f"Server configuration or data error: {e}"}), 500
    except Exception as e:
        logger.exception(f"[{session_id}] An unexpected error occurred during chat: {e}")
        return jsonify({"status": "error", "message": f"An internal server error occurred: {e}"}), 500

if __name__ == '__main__':
    # Ensure necessary mock data files exist by running the main functions of the tools
    # This is a simple way to ensure data/mock_*.json files are created if missing.
    # In a real setup, these would be managed by a data pipeline or manual setup.
    try:
        logger.info("Ensuring mock data files exist...")
        # These imports are local to ensure they don't run their main() automatically on module import
        from src.agents.tools.flight_search_tool import main as run_flight_tool_main
        from src.agents.tools.hotel_search_tool import main as run_hotel_tool_main
        from src.agents.tools.activity_search_tool import main as run_activity_tool_main
        from src.agents.tools.booking_tool import main as run_booking_tool_main # Booking tool doesn't create data, but can be run for init check

        asyncio.run(run_flight_tool_main())
        asyncio.run(run_hotel_tool_main())
        asyncio.run(run_activity_tool_main())
        # asyncio.run(run_booking_tool_main()) # Not strictly needed for data creation, but useful for init log
        logger.info("Mock data file check complete.")
    except Exception as e:
        logger.error(f"Failed to ensure mock data files exist: {e}")
        # Continue running the app, but warn that tools might fail if data is missing

    # Run the Flask application
    # For production, use a WSGI server like Gunicorn or uWSGI.
    # For development, app.run(debug=True) is fine.
    app.run(debug=True, host='0.0.0.0', port=5000)
