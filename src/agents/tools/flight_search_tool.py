# src/agents/tools/flight_search_tool.py

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.config import SIMULATED_FLIGHT_DATA_PATH # Import the path to mock data

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlightSearchTool:
    """
    A simulated tool that mimics a flight search API.
    It returns mock flight data based on query parameters,
    loading its data from a JSON file specified in config.py.
    """

    def __init__(self):
        """
        Initializes the FlightSearchTool by loading mock flight data.
        """
        self.mock_flights_data: List[Dict[str, Any]] = self._load_mock_data()
        logger.info(f"FlightSearchTool initialized. Loaded {len(self.mock_flights_data)} mock flight entries.")

    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """
        Loads mock flight data from the configured JSON file.
        """
        try:
            with open(SIMULATED_FLIGHT_DATA_PATH, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error(f"Mock flight data file '{SIMULATED_FLIGHT_DATA_PATH}' does not contain a JSON array.")
                    return []
                return data
        except FileNotFoundError:
            logger.error(f"Mock flight data file not found: {SIMULATED_FLIGHT_DATA_PATH}. Please ensure it exists.")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from mock flight data file '{SIMULATED_FLIGHT_DATA_PATH}': {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading mock flight data: {e}")
            return []

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        max_price: Optional[float] = None,
        flexible_dates_days: int = 0 # Days to search around departure_date
    ) -> List[Dict[str, Any]]:
        """
        Simulates searching for flights based on provided criteria.

        Args:
            origin (str): The departure airport code (e.g., "LAX").
            destination (str): The arrival airport code (e.g., "JFK").
            departure_date (str): The desired departure date (YYYY-MM-DD).
            return_date (Optional[str]): The desired return date (YYYY-MM-DD) for round trip.
            passengers (int): Number of passengers.
            max_price (Optional[float]): Maximum acceptable price.
            flexible_dates_days (int): Number of days to search before and after the departure_date.

        Returns:
            List[Dict[str, Any]]: A list of mock flight results matching the criteria.
                                  Each dictionary represents a flight option.
        """
        logger.info(f"Simulating flight search: {origin} -> {destination} on {departure_date} (Return: {return_date}) for {passengers} pax.")
        await asyncio.sleep(1.0) # Simulate network latency for API call

        results = []
        try:
            # Parse dates for comparison
            req_dep_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            req_ret_date = datetime.strptime(return_date, '%Y-%m-%d').date() if return_date else None

            # Define date range for flexible search
            min_dep_date = req_dep_date - timedelta(days=flexible_dates_days)
            max_dep_date = req_dep_date + timedelta(days=flexible_dates_days)

            for flight in self.mock_flights_data:
                flight_dep_date = datetime.strptime(flight['departure_date'], '%Y-%m-%d').date()
                flight_ret_date = datetime.strptime(flight['return_date'], '%Y-%m-%d').date() if flight.get('return_date') else None

                # Basic filtering logic
                match_origin = flight['origin'].upper() == origin.upper()
                match_destination = flight['destination'].upper() == destination.upper()
                match_passengers = flight['available_seats'] >= passengers
                match_price = (max_price is None) or (flight['price'] * passengers <= max_price)

                # Date flexibility check
                match_dep_date = min_dep_date <= flight_dep_date <= max_dep_date

                match_return_date = True
                if req_ret_date: # If a return date was requested
                    if not flight_ret_date: # If the mock flight is one-way but return was requested
                        match_return_date = False
                    else: # Check if mock flight's return date is within flexible range
                        min_ret_date = req_ret_date - timedelta(days=flexible_dates_days)
                        max_ret_date = req_ret_date + timedelta(days=flexible_dates_days)
                        match_return_date = min_ret_date <= flight_ret_date <= max_ret_date
                elif flight_ret_date: # If no return date was requested, but mock flight has one, still match
                    pass # One-way request can match round-trip flight

                if all([match_origin, match_destination, match_passengers, match_price, match_dep_date, match_return_date]):
                    # Return a copy to prevent external modification of internal mock data
                    results.append(flight.copy())

            logger.info(f"Found {len(results)} simulated flight results.")
            return results

        except ValueError as e:
            logger.error(f"Invalid date format or other value error in search_flights: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred during flight search simulation: {e}")
            return []

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the FlightSearchTool.
    This requires a 'mock_flights.json' file in the 'data' directory.
    """
    # Create a dummy mock_flights.json for testing if it doesn't exist
    mock_data_path = SIMULATED_FLIGHT_DATA_PATH
    if not mock_data_path.parent.exists():
        mock_data_path.parent.mkdir(parents=True, exist_ok=True)
    if not mock_data_path.exists():
        print(f"Creating dummy mock_flights.json at {mock_data_path}")
        dummy_data = [
            {"flight_id": "FL001", "origin": "LAX", "destination": "JFK", "departure_date": "2024-08-15", "departure_time": "08:00", "arrival_time": "16:00", "airline": "MockAir", "price": 350.00, "available_seats": 10, "return_date": "2024-08-20", "duration_hours": 8},
            {"flight_id": "FL002", "origin": "LAX", "destination": "JFK", "departure_date": "2024-08-16", "departure_time": "10:00", "arrival_time": "18:00", "airline": "FlySim", "price": 400.00, "available_seats": 5, "return_date": "2024-08-22", "duration_hours": 8},
            {"flight_id": "FL003", "origin": "JFK", "destination": "LAX", "departure_date": "2024-08-20", "departure_time": "09:00", "arrival_time": "17:00", "airline": "MockAir", "price": 320.00, "available_seats": 15, "return_date": None, "duration_hours": 8}, # One way
            {"flight_id": "FL004", "origin": "LAX", "destination": "CDG", "departure_date": "2024-09-01", "departure_time": "14:00", "arrival_time": "07:00", "airline": "GlobalWings", "price": 700.00, "available_seats": 20, "return_date": "2024-09-10", "duration_hours": 10},
            {"flight_id": "FL005", "origin": "LAX", "destination": "CDG", "departure_date": "2024-09-02", "departure_tim
