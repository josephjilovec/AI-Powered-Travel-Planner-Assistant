# src/utils/session_manager.py

import logging
from typing import Dict, Any, Optional, List
import time

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SessionManager:
    """
    Manages user conversation history and temporary session state for the
    AI-Powered Travel Planner Assistant.

    This manager stores session data, including extracted preferences,
    search recommendations, itineraries, and chat history for each unique user session.
    It's designed for in-memory storage for simplicity in this example,
    but could be extended to use persistent storage (e.g., Redis, database)
    for a production environment.
    """

    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initializes the SessionManager.

        Args:
            session_timeout_minutes (int): The duration in minutes after which
                                           a session will be considered stale and removed.
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout_seconds = session_timeout_minutes * 60
        logger.info(f"SessionManager initialized with timeout: {session_timeout_minutes} minutes.")

    def _clean_stale_sessions(self):
        """
        Removes sessions that have exceeded the timeout.
        This method is called internally before accessing or updating sessions.
        """
        current_time = time.time()
        stale_session_ids = [
            sid for sid, data in self.sessions.items()
            if (current_time - data.get('last_active', 0)) > self.session_timeout_seconds
        ]
        for sid in stale_session_ids:
            del self.sessions[sid]
            logger.info(f"Removed stale session: {sid}")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves the data for a specific session ID.

        Args:
            session_id (str): The unique identifier for the user session.

        Returns:
            Dict[str, Any]: The session data, or an empty dictionary if the session
                            does not exist or is stale.
        """
        self._clean_stale_sessions()
        session_data = self.sessions.get(session_id, {})
        if session_data:
            session_data['last_active'] = time.time() # Update last active time
            logger.debug(f"Retrieved session {session_id}. Last active: {session_data['last_active']}")
        else:
            logger.info(f"Session {session_id} not found or was stale. Creating new session data structure.")
            # Initialize a new session structure if not found
            self.sessions[session_id] = {
                'preferences': {},
                'recommendations': {},
                'itinerary': [],
                'chat_history': [], # For conversational agents
                'last_active': time.time()
            }
            session_data = self.sessions[session_id]
        return session_data

    def update_session(self, session_id: str, key: str, value: Any):
        """
        Updates a specific key-value pair within a session.

        Args:
            session_id (str): The unique identifier for the user session.
            key (str): The key to update (e.g., 'preferences', 'itinerary', 'chat_history').
            value (Any): The new value to set for the key.
        """
        self._clean_stale_sessions()
        if session_id not in self.sessions:
            # If session doesn't exist, create it with default structure
            self.get_session(session_id) # This will create it and set last_active
            logger.info(f"Created new session {session_id} for update operation.")

        self.sessions[session_id][key] = value
        self.sessions[session_id]['last_active'] = time.time() # Update last active time on any update
        logger.debug(f"Updated session {session_id} key '{key}'.")

    def clear_session(self, session_id: str):
        """
        Removes a specific session.

        Args:
            session_id (str): The unique identifier for the user session to remove.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
        else:
            logger.warning(f"Attempted to clear non-existent session: {session_id}")

    def add_to_chat_history(self, session_id: str, role: str, message: str):
        """
        Adds a message to the conversational chat history for a session.

        Args:
            session_id (str): The unique identifier for the user session.
            role (str): The role of the speaker ("user" or "model").
            message (str): The message content.
        """
        session_data = self.get_session(session_id) # Ensures session exists and updates last_active
        if 'chat_history' not in session_data:
            session_data['chat_history'] = []
        session_data['chat_history'].append({"role": role, "parts": [{"text": message}]})
        self.sessions[session_id]['last_active'] = time.time() # Redundant but explicit update
        logger.debug(f"Added message to chat history for session {session_id}.")

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the SessionManager.
    """
    manager = SessionManager(session_timeout_minutes=1) # Short timeout for testing

    session_id_1 = "user_abc_123"
    session_id_2 = "user_xyz_456"

    print("\n--- Test Case 1: New Session and Initial Updates ---")
    session1_data = manager.get_session(session_id_1)
    print(f"Initial Session 1: {session1_data}")

    manager.update_session(session_id_1, 'preferences', {'destination': 'Tokyo', 'budget': 3000})
    manager.add_to_chat_history(session_id_1, 'user', 'I want to go to Tokyo.')
    manager.add_to_chat_history(session_id_1, 'model', 'Great! What are your dates?')
    print(f"Updated Session 1: {manager.get_session(session_id_1)}")

    print("\n--- Test Case 2: Another Session ---")
    session2_data = manager.get_session(session_id_2)
    manager.update_session(session_id_2, 'itinerary', [{'day': 1, 'activity': 'Beach'}])
    print(f"Session 2: {manager.get_session(session_id_2)}")

    print("\n--- Test Case 3: Retrieving Existing Session ---")
    retrieved_session1 = manager.get_session(session_id_1)
    print(f"Retrieved Session 1 (again): {retrieved_session1}")

    print("\n--- Test Case 4: Simulating Stale Session (waiting for timeout) ---")
    print(f"Waiting for 65 seconds to simulate session timeout for '{session_id_1}'...")
    await asyncio.sleep(65) # Wait longer than timeout

    stale_session1_data = manager.get_session(session_id_1)
    print(f"Session 1 after timeout: {stale_session1_data}") # Should be empty or re-initialized

    print("\n--- Test Case 5: Clearing a Session ---")
    manager.clear_session(session_id_2)
    cleared_session2_data = manager.get_session(session_id_2)
    print(f"Session 2 after clearing: {cleared_session2_data}") # Should be empty or re-initialized

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
