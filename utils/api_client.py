"""
API client utility for Google Gemini API.

Handles API communication with proper error handling and retry logic.
"""

import time
from typing import Any, Dict, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
import logging

logger = logging.getLogger(__name__)


class GeminiAPIClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self) -> None:
        """Initialize the Gemini API client."""
        config = get_config()
        
        # Don't initialize if in demo mode
        if config.demo_mode:
            logger.info("Skipping API client initialization (demo mode)")
            raise RuntimeError("API client not available in demo mode")
        
        config.validate()

        try:
            genai.configure(api_key=config.api_key)
            self.model = genai.GenerativeModel(config.model_name)
            self.max_retries = config.max_retries
            self.timeout = config.timeout
            logger.info(f"Initialized Gemini API client with model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {e}", exc_info=True)
            raise

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate content using the Gemini API with retry logic.

        Args:
            prompt: The input prompt for content generation.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Generated content as a string.

        Raises:
            ValueError: If prompt is empty or invalid.
            RuntimeError: If API call fails after all retries.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        generation_config: Dict[str, Any] = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"API call attempt {attempt}/{self.max_retries}")
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                )

                if response and response.text:
                    logger.debug("API call successful")
                    return response.text.strip()
                else:
                    raise ValueError("Empty response from API")

            except google_exceptions.RetryError as e:
                last_exception = e
                logger.warning(f"Retry error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    break

            except google_exceptions.InvalidArgument as e:
                logger.error(f"Invalid argument error: {e}")
                raise ValueError(f"Invalid API request: {e}") from e

            except google_exceptions.PermissionDenied as e:
                logger.error(f"Permission denied error: {e}")
                raise RuntimeError(
                    "API key is invalid or does not have required permissions"
                ) from e

            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error on attempt {attempt}: {e}", exc_info=True)
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    break

        # If we get here, all retries failed
        error_msg = f"Failed to generate content after {self.max_retries} attempts"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_exception

