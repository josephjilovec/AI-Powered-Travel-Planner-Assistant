# src/agents/tools/activity_search_tool.py

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional

from src.config import SIMULATED_ACTIVITY_DATA_PATH # Import the path to mock data

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActivitySearchTool:
    """
    A simulated tool that mimics an activity search API.
    It returns mock activity data based on query parameters,
    loading its data from a JSON file specified in config.py.
    """

    def __init__(self):
        """
        Initializes the ActivitySearchTool by loading mock activity data.
        """
        self.mock_activities_data: List[Dict[str, Any]] = self._load_mock_data()
        logger.info(f"ActivitySearchTool initialized. Loaded {len(self.mock_activities_data)} mock activity entries.")

    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """
        Loads mock activity data from the configured JSON file.
        """
        try:
            with open(SIMULATED_ACTIVITY_DATA_PATH, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error(f"Mock activity data file '{SIMULATED_ACTIVITY_DATA_PATH}' does not contain a JSON array.")
                    return []
                return data
        except FileNotFoundError:
            logger.error(f"Mock activity data file not found: {SIMULATED_ACTIVITY_DATA_PATH}. Please ensure it exists.")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from mock activity data file '{SIMULATED_ACTIVITY_DATA_PATH}': {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading mock activity data: {e}")
            return []

    async def search_activities(
        self,
        destination: str,
        interests: Optional[List[str]] = None,
        max_price: Optional[float] = None,
        min_duration_hours: Optional[float] = None,
        max_duration_hours: Optional[float] = None,
        date: Optional[str] = None # For future specific date filtering
    ) -> List[Dict[str, Any]]:
        """
        Simulates searching for activities based on provided criteria.

        Args:
            destination (str): The city or region for the activity search.
            interests (Optional[List[str]]): List of user interests (e.g., ["museums", "food", "adventure"]).
            max_price (Optional[float]): Maximum acceptable price for an activity.
            min_duration_hours (Optional[float]): Minimum duration in hours for an activity.
            max_duration_hours (Optional[float]): Maximum duration in hours for an activity.
            date (Optional[str]): Specific date for the activity (YYYY-MM-DD). Not fully implemented in mock.

        Returns:
            List[Dict[str, Any]]: A list of mock activity results matching the criteria.
                                  Each dictionary represents an activity option.
        """
        logger.info(f"Simulating activity search in {destination} with interests: {interests}, max_price: {max_price}.")
        await asyncio.sleep(0.8) # Simulate network latency for API call

        results = []
        try:
            for activity in self.mock_activities_data:
                # Basic filtering logic
                match_destination = activity['destination'].lower() == destination.lower()
                match_price = (max_price is None) or (activity['price'] <= max_price)

                # Check duration
                match_duration = True
                if min_duration_hours is not None and activity['duration_hours'] < min_duration_hours:
                    match_duration = False
                if max_duration_hours is not None and activity['duration_hours'] > max_duration_hours:
                    match_duration = False

                # Check interests (case-insensitive, partial match for tags)
                match_interests = True
                if interests:
                    activity_tags = [tag.lower() for tag in activity.get('tags', [])]
                    for interest in interests:
                        if interest.lower() not in activity_tags: # Simple exact tag match for now
                            match_interests = False
                            break

                # Date filtering is not fully implemented in mock data, but placeholder is here
                # if date:
                #    activity_date = datetime.strptime(activity.get('date'), '%Y-%m-%d').date()
                #    if activity_date != datetime.strptime(date, '%Y-%m-%d').date():
                #        continue

                if all([match_destination, match_price, match_duration, match_interests]):
                    # Return a copy to prevent external modification of internal mock data
                    results.append(activity.copy())

            logger.info(f"Found {len(results)} simulated activity results.")
            return results

        except Exception as e:
            logger.error(f"An unexpected error occurred during activity search simulation: {e}")
            return []

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the ActivitySearchTool.
    This requires a 'mock_activities.json' file in the 'data' directory.
    """
    # Create a dummy mock_activities.json for testing if it doesn't exist
    mock_data_path = SIMULATED_ACTIVITY_DATA_PATH
    if not mock_data_path.parent.exists():
        mock_data_path.parent.mkdir(parents=True, exist_ok=True)
    if not mock_data_path.exists():
        print(f"Creating dummy mock_activities.json at {mock_data_path}")
        dummy_data = [
            {"activity_id": "A001", "name": "Eiffel Tower Tour", "destination": "Paris", "price": 50.00, "duration_hours": 2.0, "tags": ["sightseeing", "iconic", "culture"], "description": "Guided tour of the Eiffel Tower."},
            {"activity_id": "A002", "name": "Louvre Museum Visit", "destination": "Paris", "price": 20.00, "duration_hours": 3.5, "tags": ["museums", "art", "culture"], "description": "Explore world-famous art at the Louvre."},
            {"activity_id": "A003", "name": "Paris Cooking Class", "destination": "Paris", "price": 120.00, "duration_hours": 4.0, "tags": ["food", "cooking", "experience"], "description": "Learn to cook classic French dishes."},
            {"activity_id": "A004", "name": "Colosseum & Roman Forum", "destination": "Rome", "price": 60.00, "duration_hours": 3.0, "tags": ["history", "ancient", "sightseeing"], "description": "Guided tour of ancient Roman ruins."},
            {"activity_id": "A005", "name": "Rome Food Tour", "destination": "Rome", "price": 80.00, "duration_hours": 3.0, "tags": ["food", "walking", "local"], "description": "Taste local delicacies and learn about Roman cuisine."},
            {"activity_id": "A006", "name": "Vatican City Tour", "destination": "Rome", "price": 75.00, "duration_hours": 4.5, "tags": ["religion", "art", "history"], "description": "Explore St. Peter's Basilica and Vatican Museums."},
            {"activity_id": "A007", "name": "Cancun Snorkeling Adventure", "destination": "Cancun", "price": 90.00, "duration_hours": 5.0, "tags": ["adventure", "water sports", "nature"], "description": "Snorkeling trip to a coral reef."},
        ]
        with open(mock_data_path, 'w') as f:
            json.dump(dummy_data, f, indent=4)

    tool = ActivitySearchTool()

    print("\n--- Test Case 1: Paris, interests 'museums', max price 50 ---")
    activities1 = await tool.search_activities(
        destination="Paris",
        interests=["museums"],
        max_price=50.00
    )
    print(f"Results (Paris, museums, <50): {json.dumps(activities1, indent=2)}")

    print("\n--- Test Case 2: Rome, interests 'food', duration between 2-4 hours ---")
    activities2 = await tool.search_activities(
        destination="Rome",
        interests=["food"],
        min_duration_hours=2.0,
        max_duration_hours=4.0
    )
    print(f"Results (Rome, food, 2-4h): {json.dumps(activities2, indent=2)}")

    print("\n--- Test Case 3: Cancun, interests 'adventure', no price limit ---")
    activities3 = await tool.search_activities(
        destination="Cancun",
        interests=["adventure"]
    )
    print(f"Results (Cancun, adventure): {json.dumps(activities3, indent=2)}")

    print("\n--- Test Case 4: Paris, interests 'hiking' (no match) ---")
    activities4 = await tool.search_activities(
        destination="Paris",
        interests=["hiking"]
    )
    print(f"Results (Paris, hiking): {json.dumps(activities4, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
