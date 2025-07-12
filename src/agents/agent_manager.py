# src/agents/agent_manager.py

import logging
from typing import Dict, Any, Callable, List, Optional

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentManager:
    """
    The AgentManager is the central orchestrator class responsible for managing
    the lifecycle, communication, and task assignment for all AI agents within
    the AI-Powered Travel Planner Assistant system.

    It provides methods to register different types of agents, dispatch tasks
    to them based on their capabilities, and collect the results of their operations.
    """

    def __init__(self):
        """
        Initializes the AgentManager with an empty dictionary to store registered agents.
        Agents are stored by their unique name, and their type/role is also tracked.
        """
        self.agents: Dict[str, Any] = {}  # Stores agent instances by name
        self.agent_types: Dict[str, str] = {} # Maps agent name to agent type (e.g., 'preference_agent', 'search_agent')
        logger.info("AgentManager initialized.")

    def register_agent(self, name: str, agent_instance: Any, agent_type: str):
        """
        Registers an AI agent with the manager.

        Args:
            name (str): A unique name for the agent (e.g., "preference_collector_v1").
            agent_instance (Any): The actual instance of the agent class. This instance
                                  is expected to have an asynchronous 'process_task' method.
            agent_type (str): The type or role of the agent (e.g., "preference_collection",
                              "flight_search", "accommodation_search", "itinerary_creation",
                              "booking_support"). This is used for task dispatching.
        Raises:
            ValueError: If an agent with the given name is already registered.
        """
        if name in self.agents:
            logger.error(f"Agent with name '{name}' is already registered.")
            raise ValueError(f"Agent with name '{name}' is already registered.")

        self.agents[name] = agent_instance
        self.agent_types[name] = agent_type
        logger.info(f"Agent '{name}' of type '{agent_type}' registered successfully.")

    def get_agent(self, name: str) -> Optional[Any]:
        """
        Retrieves a registered agent by its name.

        Args:
            name (str): The unique name of the agent.

        Returns:
            Optional[Any]: The agent instance if found, otherwise None.
        """
        agent = self.agents.get(name)
        if not agent:
            logger.warning(f"Attempted to retrieve unregistered agent: '{name}'.")
        return agent

    def get_agents_by_type(self, agent_type: str) -> List[Any]:
        """
        Retrieves all registered agents of a specific type.

        Args:
            agent_type (str): The type or role of the agents to retrieve.

        Returns:
            List[Any]: A list of agent instances matching the given type.
        """
        return [
            agent_instance
            for name, agent_instance in self.agents.items()
            if self.agent_types.get(name) == agent_type
        ]

    async def dispatch_task(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches a task to a specific registered agent.
        This method assumes agents have an asynchronous `process_task` method.

        Args:
            agent_name (str): The unique name of the agent to dispatch the task to.
            task_data (Dict[str, Any]): A dictionary containing the data pertinent to the task.
                                         The structure of this data depends on the agent's type.

        Returns:
            Dict[str, Any]: The result of the task processed by the agent.
                            The structure of the result depends on the agent's type.

        Raises:
            ValueError: If the specified agent is not registered.
            AttributeError: If the agent does not have a 'process_task' method.
            Exception: If the agent's process_task method fails.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            logger.error(f"Attempted to dispatch task to unregistered agent: '{agent_name}'.")
            raise ValueError(f"Agent '{agent_name}' is not registered.")

        logger.info(f"Dispatching task to agent '{agent_name}' (type: {self.agent_types.get(agent_name)}).")
        try:
            # Agents are expected to have an asynchronous method named 'process_task'
            if hasattr(agent, 'process_task') and callable(agent.process_task):
                result = await agent.process_task(task_data)
                logger.info(f"Task dispatched to '{agent_name}' completed.")
                return result
            else:
                logger.error(f"Agent '{agent_name}' does not have a 'process_task' method.")
                raise AttributeError(f"Agent '{agent_name}' does not have a 'process_task' method.")
        except Exception as e:
            logger.exception(f"Error processing task by agent '{agent_name}': {e}")
            raise

    def list_agents(self) -> Dict[str, str]:
        """
        Lists all registered agents and their types.

        Returns:
            Dict[str, str]: A dictionary where keys are agent names and values are agent types.
        """
        return self.agent_types

# Example Usage (for demonstration purposes, not part of the module itself)
async def main():
    """
    Demonstrates how to use the AgentManager.
    This would typically be part of the orchestrator in the Applications Layer.
    """
    class MockAgent:
        def __init__(self, name):
            self.name = name
        async def process_task(self, data):
            logger.info(f"{self.name} processing task: {data.get('query')}")
            # Simulate agent specific logic
            if self.name == "PreferenceCollector":
                return {"status": "preferences_collected", "preferences": {"destination": "Paris"}}
            elif self.name == "FlightSearcher":
                return {"status": "flights_found", "flights": ["FL101", "FL102"]}
            return {"status": "completed", "result": "mock_result"}

    manager = AgentManager()

    # Register mock agents
    pref_agent = MockAgent("PreferenceCollector")
    flight_agent = MockAgent("FlightSearcher")
    manager.register_agent("PreferenceCollector", pref_agent, "preference_collection")
    manager.register_agent("FlightSearcher", flight_agent, "flight_search")

    print("\nRegistered Agents:", manager.list_agents())

    # Dispatch tasks
    try:
        pref_result = await manager.dispatch_task(
            "PreferenceCollector", {"query": "I want a relaxing beach vacation."}
        )
        print("\nPreference Collection Result:", pref_result)

        flight_result = await manager.dispatch_task(
            "FlightSearcher", {"query": "flights to Paris", "preferences": pref_result.get("preferences")}
        )
        print("\nFlight Search Result:", flight_result)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
