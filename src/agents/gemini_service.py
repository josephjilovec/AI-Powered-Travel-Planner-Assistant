# src/agents/gemini_service.py

import os
import httpx # For asynchronous HTTP requests
import logging
import json # For parsing JSON responses
from typing import Dict, Any, List, Optional

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiService:
    """
    A utility class to encapsulate all interactions with the Google Gemini API.
    It handles API key management, prompt construction, and making generateContent
    calls to the gemini-2.0-flash model, including robust error handling.
    """

    def __init__(self):
        """
        Initializes the GeminiService by loading the API key from environment variables.
        """
        self.api_key: Optional[str] = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY environment variable is not set. Gemini API calls will fail.")
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file.")

        self.api_url: str = (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        )
        self.client = httpx.AsyncClient(timeout=60.0) # Initialize an async HTTP client with a generous timeout
        logger.info("GeminiService initialized.")

    async def call_gemini_api(self, chat_history: List[Dict[str, Any]], prompt: str,
                              response_schema: Optional[Dict[str, Any]] = None) -> str:
        """
        Makes an asynchronous call to the Google Gemini API to generate content.

        Args:
            chat_history (List[Dict[str, Any]]): A list of message objects representing the
                                                  conversation history. Each object should
                                                  have a 'role' (e.g., "user", "model")
                                                  and 'parts' (e.g., [{ "text": "message" }]).
                                                  This is used to maintain conversational context.
            prompt (str): The specific prompt for the current turn. This will be added
                          to the end of the chat_history for the API call.
            response_schema (Optional[Dict[str, Any]]): An optional JSON schema to guide the
                                                        model's response structure.

        Returns:
            str: The generated text response from the Gemini model. If `response_schema` is
                 provided, this will be a JSON string.

        Raises:
            httpx.RequestError: If a network-related error occurs during the API call.
            httpx.HTTPStatusError: If the API call returns an unsuccessful HTTP status code.
            ValueError: If the API key is missing or the response structure is unexpected.
            Exception: For any other unexpected errors.
        """
        if not self.api_key:
            logger.error("Attempted to call Gemini API without a configured API key.")
            raise ValueError("Gemini API key is not set.")

        # Construct the full conversation history for the API payload
        # The new user prompt is added as the last turn.
        full_conversation_contents = [
            *chat_history,
            {"role": "user", "parts": [{"text": prompt}]}
        ]

        payload = {
            "contents": full_conversation_contents,
            "generationConfig": {
                "temperature": 0.7, # Adjust creativity (0.0 - 1.0)
                "maxOutputTokens": 1024, # Max tokens in the response
            },
        }

        if response_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            payload["generationConfig"]["responseSchema"] = response_schema

        logger.info(f"Sending request to Gemini API. Prompt length: {len(prompt)} chars. Schema provided: {bool(response_schema)}")
        try:
            response = await self.client.post(self.api_url, json=payload)
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses

            result = response.json()

            # Validate the structure of the Gemini API response
            if result and result.get("candidates") and len(result["candidates"]) > 0 and \
               result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts") and \
               len(result["candidates"][0]["content"]["parts"]) > 0 and \
               result["candidates"][0]["content"]["parts"][0].get("text"):
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                logger.info("Successfully received response from Gemini API.")
                return generated_text
            else:
                logger.warning(f"Unexpected API response structure: {result}")
                raise ValueError("Unexpected response structure from Gemini API. No text content found.")

        except httpx.RequestError as e:
            logger.error(f"Network or request error during Gemini API call: {e}")
            raise httpx.RequestError(f"Network or request error: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during Gemini API call: {e.response.status_code} - {e.response.text}")
            raise httpx.HTTPStatusError(f"API returned error status {e.response.status_code}: {e.response.text}", request=e.request, response=e.response)
        except Exception as e:
            logger.error(f"An unexpected error occurred during Gemini API call: {e}")
            raise Exception(f"An unexpected error occurred: {e}")

# Example Usage (for demonstration purposes, not part of the module itself)
async def main():
    """
    Demonstrates how to use the GeminiService.
    """
    # Set a dummy API key for local testing if not already set in environment
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = 'YOUR_MOCK_GEMINI_API_KEY' # Replace with a real key for actual calls

    try:
        gemini_service = GeminiService()

        # Example 1: Simple text generation
        chat_history_text = []
        user_prompt_text = "What are the top 3 things to do in Paris?"
        logger.info(f"\n--- Testing GeminiService (Text Gen) with prompt: '{user_prompt_text}' ---")
        response_text = await gemini_service.call_gemini_api(chat_history_text, user_prompt_text)
        print(f"\nGemini Text Response:\n{response_text}")

        # Example 2: Structured JSON generation
        chat_history_json = []
        user_prompt_json = "Give me a list of 2 popular tourist attractions in Rome with their opening hours."
        json_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "attraction_name": {"type": "STRING"},
                    "opening_hours": {"type": "STRING"}
                },
                "required": ["attraction_name", "opening_hours"]
            }
        }
        logger.info(f"\n--- Testing GeminiService (JSON Gen) with prompt: '{user_prompt_json}' ---")
        response_json_str = await gemini_service.call_gemini_api(chat_history_json, user_prompt_json, response_schema=json_schema)
        print(f"\nGemini JSON String Response:\n{response_json_str}")
        try:
            parsed_json = json.loads(response_json_str)
            print(f"Parsed JSON: {json.dumps(parsed_json, indent=2)}")
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")


    except ValueError as e:
        print(f"Configuration Error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"API Error (HTTP Status): {e}")
    except httpx.RequestError as e:
        print(f"Network Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
