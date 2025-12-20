"""
Base agent class for AI-Powered Travel Planner Assistant.

Provides common functionality for all agent types.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_config
from utils.api_client import GeminiAPIClient
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all travel planner agents."""

    def __init__(self, name: str) -> None:
        """
        Initialize the base agent.

        Args:
            name: Name of the agent.
        """
        self.name = name
        self.config = get_config()
        
        # Only initialize API client if not in demo mode
        if not self.config.demo_mode:
            try:
                self.api_client = GeminiAPIClient()
            except Exception as e:
                logger.warning(f"Failed to initialize API client: {e}. Using demo mode.")
                self.config._demo_mode = True
                self.api_client = None
        else:
            self.api_client = None
            
        logger.info(f"Initialized {self.name} agent (Demo Mode: {self.config.demo_mode})")

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.

        Args:
            input_data: Input data dictionary.

        Returns:
            Results dictionary.
        """
        pass

    def _create_prompt(self, system_prompt: str, user_input: str) -> str:
        """
        Create a formatted prompt for the API.

        Args:
            system_prompt: System-level instructions.
            user_input: User-provided input.

        Returns:
            Formatted prompt string.
        """
        return f"{system_prompt}\n\nUser Input: {user_input}\n\nResponse:"

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse API response into structured format.

        Args:
            response: Raw API response string.

        Returns:
            Parsed response dictionary.
        """
        # Default implementation - can be overridden by subclasses
        return {"response": response, "raw": response}

