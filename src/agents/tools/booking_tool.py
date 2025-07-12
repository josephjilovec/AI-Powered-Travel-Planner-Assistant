# src/agents/tools/booking_tool.py

import logging
import asyncio
import uuid # For generating unique booking IDs
from typing import Dict, Any, Optional

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookingTool:
    """
    A simulated tool that mimics a booking confirmation API.
    It generates mock booking IDs and confirmation statuses for various
    travel services (flights, hotels, activities).
    """

    def __init__(self):
        """
        Initializes the BookingTool.
        In a real application, this might connect to a database or external booking system.
        For simulation, it just prepares for generating mock confirmations.
        """
        logger.info("BookingTool initialized. Ready to simulate bookings.")

    async def confirm_booking(
        self,
        item_type: str, # e.g., "flight", "hotel", "activity"
        item_details: Dict[str, Any], # Details of the item to be booked (e.g., flight_id, hotel_id)
        user_info: Dict[str, Any], # Mock user information (e.g., {"name": "John Doe", "email": "john.doe@example.com"})
        total_price: float
    ) -> Dict[str, Any]:
        """
        Simulates the confirmation of a booking for a given item.

        Args:
            item_type (str): The type of item being booked (e.g., "flight", "hotel", "activity").
            item_details (Dict[str, Any]): A dictionary containing specific details of the item
                                           being booked (e.g., flight_id, hotel_id, activity_id,
                                           dates, destination, etc.).
            user_info (Dict[str, Any]): A dictionary containing mock user details
                                         necessary for booking (e.g., name, email).
            total_price (float): The total price for the booking.

        Returns:
            Dict[str, Any]: A dictionary containing the booking confirmation details:
                            - 'status': "confirmed" or "failed".
                            - 'booking_id': A unique identifier for the booking (if confirmed).
                            - 'confirmation_message': A user-friendly message.
                            - 'booked_item_details': The details of the item that was "booked".
                            - 'user_contact': The user info used for booking.
                            - 'price_paid': The total price.
        """
        logger.info(f"Simulating booking confirmation for {item_type} (ID: {item_details.get('id', 'N/A')}) for {user_info.get('name', 'N/A')}.")
        await asyncio.sleep(1.5) # Simulate network latency and processing time for booking

        # Simulate a random chance of booking failure for realism
        if random.random() < 0.05: # 5% chance of failure
            logger.warning(f"Simulated booking failed for {item_type} (ID: {item_details.get('id', 'N/A')}).")
            return {
                "status": "failed",
                "booking_id": None,
                "confirmation_message": f"Failed to book {item_type}. Please try again or contact support.",
                "booked_item_details": item_details,
                "user_contact": user_info,
                "price_paid": total_price,
                "error": "Simulated booking system error or unavailability."
            }

        booking_id = str(uuid.uuid4()) # Generate a unique booking ID
        confirmation_message = (
            f"Your {item_type} booking (ID: {booking_id}) has been confirmed! "
            f"A confirmation email has been sent to {user_info.get('email', 'your provided email')}. "
            f"Total price: ${total_price:.2f}."
        )

        logger.info(f"Simulated booking confirmed for {item_type} with ID: {booking_id}.")
        return {
            "status": "confirmed",
            "booking_id": booking_id,
            "confirmation_message": confirmation_message,
            "booked_item_details": item_details,
            "user_contact": user_info,
            "price_paid": total_price
        }

# Example Usage (for demonstration purposes)
async def main():
    """
    Demonstrates how to use the BookingTool.
    """
    tool = BookingTool()

    mock_user = {"name": "Alice Smith", "email": "alice.smith@example.com"}

    print("\n--- Test Case 1: Booking a Flight ---")
    mock_flight = {
        "id": "FL007",
        "origin": "SFO",
        "destination": "NYC",
        "departure_date": "2024-12-01",
        "price": 450.00
    }
    flight_booking_result = await tool.confirm_booking(
        item_type="flight",
        item_details=mock_flight,
        user_info=mock_user,
        total_price=450.00
    )
    print(f"Flight Booking Result: {json.dumps(flight_booking_result, indent=2)}")

    print("\n--- Test Case 2: Booking a Hotel ---")
    mock_hotel = {
        "id": "H006",
        "name": "Cozy Inn",
        "destination": "London",
        "check_in": "2025-01-10",
        "check_out": "2025-01-15",
        "price_per_night": 150.00
    }
    hotel_booking_result = await tool.confirm_booking(
        item_type="hotel",
        item_details=mock_hotel,
        user_info=mock_user,
        total_price=150.00 * 5 # 5 nights
    )
    print(f"Hotel Booking Result: {json.dumps(hotel_booking_result, indent=2)}")

    print("\n--- Test Case 3: Booking an Activity ---")
    mock_activity = {
        "id": "A008",
        "name": "City Bike Tour",
        "destination": "Berlin",
        "date": "2024-11-20",
        "price": 75.00
    }
    activity_booking_result = await tool.confirm_booking(
        item_type="activity",
        item_details=mock_activity,
        user_info=mock_user,
        total_price=75.00
    )
    print(f"Activity Booking Result: {json.dumps(activity_booking_result, indent=2)}")

    print("\n--- Test Case 4: Simulating a potential booking failure ---")
    # This might fail due to the random.random() < 0.05 condition
    mock_item_to_fail = {
        "id": "FAIL001",
        "type": "simulated_failure_item",
        "price": 100.00
    }
    failure_result = await tool.confirm_booking(
        item_type="test_fail",
        item_details=mock_item_to_fail,
        user_info=mock_user,
        total_price=100.00
    )
    print(f"Simulated Failure Result: {json.dumps(failure_result, indent=2)}")


if __name__ == "__main__":
    import asyncio
    import random # Import random for the failure simulation
    asyncio.run(main())
