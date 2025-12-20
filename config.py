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
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from Streamlit secrets or environment variables."""
        try:
            # Try to get API key from Streamlit secrets (for Streamlit Cloud)
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                self._api_key = st.secrets["GEMINI_API_KEY"]
                logger.info("Loaded API key from Streamlit secrets")
            # Fallback to environment variable (for local development)
            elif "GEMINI_API_KEY" in os.environ:
                self._api_key = os.environ["GEMINI_API_KEY"]
                logger.info("Loaded API key from environment variable")
            else:
                logger.warning("API key not found in secrets or environment variables")

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
            raise

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

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Set it in Streamlit secrets or as an environment variable."
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

