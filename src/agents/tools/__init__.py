# src/agents/tools/__init__.py

# This file makes the 'tools' directory a Python package.
# It also allows for convenient imports of the tool classes directly from 'src.agents.tools'.

from .flight_search_tool import FlightSearchTool
from .hotel_search_tool import HotelSearchTool
from .activity_search_tool import ActivitySearchTool
from .booking_tool import BookingTool

# You can optionally define __all__ to control what gets imported with 'from .tools import *'
__all__ = [
    "FlightSearchTool",
    "HotelSearchTool",
    "ActivitySearchTool",
    "BookingTool",
]

# A simple log to indicate the package is loaded
import logging
logger = logging.getLogger(__name__)
logger.info("Agents tools package initialized.")
