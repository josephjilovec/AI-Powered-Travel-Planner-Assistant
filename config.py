"""
Configuration module for AI-Powered Travel Planner Assistant.

This module handles environment variables and configuration settings,
prioritizing Streamlit secrets for deployment on Streamlit Cloud.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import streamlit as st

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for managing application settings."""

    def __init__(self) -> None:
        """Initialize configuration with Streamlit secrets or environment variables."""
        self._api_key: Optional[str] = None
        self._model_name: str = "gemini-pro"
        self._max_retries: int = 3
        self._timeout: int = 30
        self._demo_mode: bool = False
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from Streamlit secrets or environment variables."""
        try:
            # Check for demo mode flag
            demo_mode_env = os.environ.get("DEMO_MODE", "false").lower()
            demo_mode_secret = False
            if hasattr(st, "secrets"):
                demo_mode_secret = st.secrets.get("DEMO_MODE", "false").lower() == "true"
            
            self._demo_mode = demo_mode_env == "true" or demo_mode_secret
            
            # Try to get API key from Streamlit secrets (for Streamlit Cloud)
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
                # Allow placeholder/demo keys
                if api_key and api_key.strip() and api_key.lower() not in ["demo", "placeholder", "your_api_key_here"]:
                    self._api_key = api_key
                    logger.info("Loaded API key from Streamlit secrets")
                else:
                    logger.info("Demo/placeholder API key detected, enabling demo mode")
                    self._demo_mode = True
            # Fallback to environment variable (for local development)
            elif "GEMINI_API_KEY" in os.environ:
                api_key = os.environ["GEMINI_API_KEY"]
                if api_key and api_key.strip() and api_key.lower() not in ["demo", "placeholder", "your_api_key_here"]:
                    self._api_key = api_key
                    logger.info("Loaded API key from environment variable")
                else:
                    logger.info("Demo/placeholder API key detected, enabling demo mode")
                    self._demo_mode = True
            else:
                logger.info("API key not found - enabling demo mode")
                self._demo_mode = True

            # Load optional configuration
            if hasattr(st, "secrets"):
                self._model_name = st.secrets.get("GEMINI_MODEL", "gemini-pro")
                self._max_retries = int(st.secrets.get("MAX_RETRIES", 3))
                self._timeout = int(st.secrets.get("TIMEOUT", 30))
            else:
                self._model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")
                self._max_retries = int(os.environ.get("MAX_RETRIES", 3))
                self._timeout = int(os.environ.get("TIMEOUT", 30))

        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            # Default to demo mode on error
            self._demo_mode = True

    @property
    def api_key(self) -> Optional[str]:
        """Get the Gemini API key."""
        return self._api_key

    @property
    def model_name(self) -> str:
        """Get the Gemini model name."""
        return self._model_name

    @property
    def max_retries(self) -> int:
        """Get the maximum number of retries for API calls."""
        return self._max_retries

    @property
    def timeout(self) -> int:
        """Get the timeout for API calls in seconds."""
        return self._timeout

    @property
    def demo_mode(self) -> bool:
        """Check if demo mode is enabled."""
        return self._demo_mode

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        # In demo mode, API key is not required
        if self._demo_mode:
            logger.info("Running in DEMO MODE - using mock data")
            return True
        
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Set it in Streamlit secrets or as an environment variable. "
                "Or set DEMO_MODE=true to use demo/mock data."
            )
        return True


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config

