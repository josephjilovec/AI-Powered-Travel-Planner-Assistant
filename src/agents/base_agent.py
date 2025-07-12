# src/agents/base_agent.py

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    An abstract base class (ABC) that defines the common interface and
    attributes for all AI agents within the AI-Powered Travel Planner Assistant.

    All concrete agent implementations (e.g., PreferenceAgent, SearchAgent,
    ItineraryAgent) must inherit from this class and implement its abstract methods.
    """

    def __init__(self, agent_id: str, persona: str, description: str):
        """
        Initializes the BaseAgent with a unique ID, a descriptive persona,
        and a brief description of its role.

        Args:
            agent_id (str): A unique identifier for the agent instance.
            persona (str): A string describing the agent's personality or role
                           (e.g., "User Preference Analyst", "Global Flight Finder").
            description (str): A brief explanation of what this agent does.
        """
        if not agent_id:
            raise ValueError("Agent ID cannot be empty.")
        if not persona:
            raise ValueError("Agent persona cannot be empty.")
        if not description:
            raise ValueError("Agent description cannot be empty.")

        self.agent_id: str = agent_id
        self.persona: str = persona
        self.description: str = description
        logger.info(f"BaseAgent '{self.agent_id}' initialized with persona: '{self.persona}'.")

    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to be implemented by concrete agent classes.
        This method defines the core asynchronous logic for how an agent processes a given task.

        Args:
            task_data (Dict[str, Any]): A dictionary containing the data relevant to the task.
                                         The structure will vary depending on the agent's specific role.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the task processing.
                            The structure of the result will depend on the agent's specific role.

        Raises:
            NotImplementedError: If a concrete agent does not implement this method.
            Exception: Any specific exceptions related to the agent's task processing.
        """
        raise NotImplementedError("Subclasses must implement the process_task method.")

    def get_info(self) -> Dict[str, str]:
        """
        Returns basic information about the agent.

        Returns:
            Dict[str, str]: A dictionary containing the agent's ID, persona, and description.
        """
        return {
            "agent_id": self.agent_id,
            "persona": self.persona,
            "description": self.description
        }

    async def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        A general method for an agent to formulate a textual response.
        This can be overridden by subclasses for more complex response generation
        (e.g., using an LLM to craft conversational replies).
        For the base class, it's a simple echo with persona.

        Args:
            message (str): The input message or data to respond to.
            context (Optional[Dict[str, Any]]): Additional context for generating the response.

        Returns:
            str: The formatted response from the agent.
        """
        logger.debug(f"Agent '{self.agent_id}' responding to message: '{message}'.")
        # Default response format, can be enhanced by subclasses
        response = f"[{self.persona} ({self.agent_id})] received: '{message}'."
        if context:
            response += f" Context: {context}"
        return response

# Example Usage (for demonstration purposes, not part of the module itself)
async def main():
    """
    Demonstrates how to create and use a concrete agent inheriting from BaseAgent.
    """
    class ConcreteTravelAgent(BaseAgent):
        def __init__(self, agent_id: str):
            super().__init__(agent_id,
                             persona="Mock Travel Assistant",
                             description="A mock agent for travel planning tasks.")

        async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Example implementation of process_task for a concrete agent.
            """
            logger.info(f"{self.agent_id} is processing task: {task_data}")
            processed_data = {
                "original_task": task_data,
                "status": "processed",
                "result_summary": f"Task for {task_data.get('type')} completed."
            }
            return processed_data

    try:
        example_agent = ConcreteTravelAgent("mock_agent_001")
        print(f"Agent Info: {example_agent.get_info()}")

        task = {"type": "flight_search", "destination": "Tokyo", "date": "2024-12-25"}
        result = await example_agent.process_task(task)
        print(f"Task Result: {result}")

        response_msg = await example_agent.respond("User asked about flight prices.")
        print(f"Agent Response: {response_msg}")

        # This will raise NotImplementedError if not implemented
        # class IncompleteAgent(BaseAgent):
        #     def __init__(self, agent_id: str):
        #         super().__init__(agent_id, "Incomplete", "Just for testing abstract method.")
        # incomplete_agent = IncompleteAgent("incomplete_001")
        # await incomplete_agent.process_task({"data": "test"})

    except ValueError as e:
        print(f"Initialization Error: {e}")
    except NotImplementedError as e:
        print(f"Abstract Method Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
