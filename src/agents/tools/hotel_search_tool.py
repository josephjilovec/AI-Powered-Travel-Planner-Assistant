# src/agents/tools/hotel_search_tool.py

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.config import SIMULATED_ACCOMMODATION_DATA_PATH # Import the path to mock data

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HotelSearchTool:
    """
    A simulated tool that mimics a hotel search API.
    It returns mock hotel data based on query parameters,
    loading its data from a JSON file specified in config.py.
    """

    def __init__(self):
        """
        Initializes the HotelSearchTool by loading mock hotel data.
        """
        self.mock_hotels_data: List[Dict[str, Any]] = self._load_mock_data()
        logger.info(f"HotelSearchTool initialized. Loaded {len(self.mock_hotels_data)} mock hotel entries.")

    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """
        Loads mock hotel data from the configured JSON file.
        """
        try:
            with open(SIMULATED_ACCOMMODATION_DATA_PATH, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error(f"Mock hotel data file '{SIMULATED_ACCOMMODATION_DATA_PATH}' does not contain a JSON array.")
                    return []
                return data
        except FileNotFoundError:
            logger.error(f"Mock hotel data file not found: {SIMULATED_ACCOMMODATION_DATA_PATH}. Please ensure it exists.")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from mock hotel data file '{SIMULATED_ACCOMMODATION_DATA_PATH}': {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading mock hotel data: {e}")
            return []

    async def search_hotels(
        self,
        destination: str,
        check_in_date: str,
        check_out_date: str,
        guests: int = 1,
        max_price_per_night: Optional[float] = None,
        amenities: Optional[List[str]] = None,
        min_rating: Optional[float] = None # e.g., 4.0 for 4 stars
    ) -> List[Dict[str, Any]]:
        """
        Simulates searching for hotels based on provided criteria.

        Args:
            destination (str): The city or region for the hotel search.
            check_in_date (str): The desired check-in date (YYYY-MM-DD).
            check_out_date (str): The desired check-out date (YYYY-MM-DD).
            guests (int): Number of guests.
            max_price_per_night (Optional[float]): Maximum acceptable price per night.
            amenities (Optional[List[str]]): List of required amenities (e.g., ["pool", "wifi"]).
            min_rating (Optional[float]): Minimum star rating (e.g., 3.0, 4.5).

        Returns:
            List[Dict[str, Any]]: A list of mock hotel results matching the criteria.
                                  Each dictionary represents a hotel option.
        """
        logger.info(f"Simulating hotel search in {destination} from {check_in_date} to {check_out_date} for {guests} guests.")
        await asyncio.sleep(1.0) # Simulate network latency for API call

        results = []
        try:
            req_check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            req_check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()

            for hotel in self.mock_hotels_data:
                # Basic filtering logic
                match_destination = hotel['destination'].lower() == destination.lower()
                match_guests = hotel['max_guests_per_room'] >= guests
                match_price = (max_price_per_night is None) or (hotel['price_per_night'] <= max_price_per_night)
                match_rating = (min_rating is None) or (hotel['rating'] >= min_rating)

                # Check amenities
                match_amenities = True
                if amenities:
                    for amenity in amenities:
                        if amenity.lower() not in [a.lower() for a in hotel.get('amenities', [])]:
                            match_amenities = False
                            break

                # Check date availability (simplified: assumes hotel is always available if dates are within range)
                # In a real system, this would involve checking specific room availability for the dates.
                # For simulation, we'll just ensure check-in is not in the past and check-out is after check-in.
                is_available_dates = req_check_in >= datetime.now().date() and req_check_out > req_check_in

                if all([match_destination, match_guests, match_price, match_rating, match_amenities, is_available_dates]):
                    # Return a copy to prevent external modification of internal mock data
                    results.append(hotel.copy())

            logger.info(f"Found {len(results)} simulated hotel results.")
            return results

        except ValueError as e:
            logger.error(f"Invalid date format or other value error in search_hotels: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred during hotel search simulation: {e}")
            return []

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the HotelSearchTool.
    This requires a 'mock_accommodations.json' file in the 'data' directory.
    """
    # Create a dummy mock_accommodations.json for testing if it doesn't exist
    mock_data_path = SIMULATED_ACCOMMODATION_DATA_PATH
    if not mock_data_path.parent.exists():
        mock_data_path.parent.mkdir(parents=True, exist_ok=True)
    if not mock_data_path.exists():
        print(f"Creating dummy mock_accommodations.json at {mock_data_path}")
        dummy_data = [
            {"hotel_id": "H001", "name": "Grand City Hotel", "destination": "Paris", "rating": 4.5, "price_per_night": 250.00, "max_guests_per_room": 2, "amenities": ["wifi", "pool", "gym"], "description": "Luxury hotel in city center."},
            {"hotel_id": "H002", "name": "Budget Stay Paris", "destination": "Paris", "rating": 3.0, "price_per_night": 100.00, "max_guests_per_room": 3, "amenities": ["wifi"], "description": "Affordable and cozy stay."},
            {"hotel_id": "H003", "name": "Beach Resort Cancun", "destination": "Cancun", "rating": 5.0, "price_per_night": 400.00, "max_guests_per_room": 4, "amenities": ["wifi", "pool", "beach access", "spa"], "description": "All-inclusive beachfront resort."},
            {"hotel_id": "H004", "name": "Downtown Hostel Rome", "destination": "Rome", "rating": 2.5, "price_per_night": 50.00, "max_guests_per_room": 1, "amenities": ["wifi", "shared kitchen"], "description": "Lively hostel for solo travelers."},
            {"hotel_id": "H005", "name": "Historic Inn Rome", "destination": "Rome", "rating": 4.0, "price_per_night": 180.00, "max_guests_per_room": 2, "amenities": ["wifi", "breakfast"], "description": "Charming inn near ancient sites."},
        ]
        with open(mock_data_path, 'w') as f:
            json.dump(dummy_data, f, indent=4)

    tool = HotelSearchTool()

    print("\n--- Test Case 1: Paris, 2 guests, max price 300, with pool ---")
    hotels1 = await tool.search_hotels(
        destination="Paris",
        check_in_date="2024-09-10",
        check_out_date="2024-09-15",
        guests=2,
        max_price_per_night=300.00,
        amenities=["pool"]
    )
    print(f"Results (Paris, 2pax, <300, pool): {json.dumps(hotels1, indent=2)}")

    print("\n--- Test Case 2: Cancun, 3 guests, min 4.5 rating ---")
    hotels2 = await tool.search_hotels(
        destination="Cancun",
        check_in_date="2024-10-01",
        check_out_date="2024-
