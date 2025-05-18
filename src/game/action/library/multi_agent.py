"""Multi-agent communication and memory patterns defined as tools"""

from game.action import tool
from game.action.context import ActionContext
from game.action.library.default import logging
from game.memory.dict_memory import DictMemory


@tool(tool_name="call_agent")
def call_agent_message_passing(
    action_context: ActionContext, agent_name: str, task: str
) -> dict:
    """
    Invoke another agent to perform a specific task using the `Message Passing` pattern which is the simplest form
    of agent interaction. One agent sends a request and receives a response.

    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform

    Returns:
        The result from the invoked agent's final memory
    """
    logging.debug(f"Switching to agent: '{agent_name}' for the task: '{task}'")

    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        error_message = f"No agent registry found in context!"
        logging.error(error_message)
        raise ValueError(error_message)

    # Get the agent's run function from the registry
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        error_message = f"Agent '{agent_name}' not found in registry: {" ".join(agent_registry.get_agent_descriptions())}"
        logging.error(error_message)
        raise ValueError(error_message)

    logging.debug(f"Handing over to '{agent.name}': '{agent.description}'")

    # Create a new memory instance for the invoked agent
    # invoked_memory = DictMemory()

    try:
        # Run the agent with the provided task
        result_memory = agent.run(user_input=task)

        # Get the last memory item as the result
        if result_memory.items:
            last_memory = result_memory.items[-1]
            result = {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content"),
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result
        else:
            result = {
                "success": False,
                "error": "Agent failed to run.",
                "agent": agent_name,
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result

    except Exception as e:
        logging.debug(
            f"Switching from agent: '{agent_name}' with error: {e.__class__.__name__}('{e}')"
        )
        return {"success": False, "error": str(e), "agent": agent_name}


@tool(tool_name="call_agent")
def call_agent_with_reflection(
    action_context: ActionContext, agent_name: str, task: str
) -> dict:
    """
    Invoke another agent to perform a specific task using the `Memory Reflection` pattern in which the caller agent
    receives the full memory of the invoked agent.

    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform

    Returns:
        The result from the invoked agent's final memory
    """
    logging.debug(f"Switching to agent: '{agent_name}' for the task: '{task}'")

    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        error_message = f"No agent registry found in context!"
        logging.error(error_message)
        raise ValueError(error_message)

    # Get the agent's run function from the registry
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        error_message = f"Agent '{agent_name}' not found in registry: {" ".join(agent_registry.get_agent_descriptions())}"
        logging.error(error_message)
        raise ValueError(error_message)

    logging.debug(f"Handing over to '{agent.name}': '{agent.description}'")

    try:
        # Run the agent with the provided task
        result_memory = agent.run(user_input=task)

        # Get the last memory item as the result
        if result_memory.items:
            # Get the caller's memory
            caller_memory = action_context.get_memory()
            # Add all memories from invoked agent to caller,
            # although we could leave off the last memory to
            # avoid duplication
            for memory_item in result_memory.items:
                caller_memory.add_memory(
                    {
                        "type": f"{agent_name}_thought",  # Mark source of memory
                        "content": memory_item["content"],
                    }
                )

            last_memory = result_memory.items[-1]
            result = {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content"),
                "memories_added": len(result_memory.items),
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result
        else:
            result = {
                "success": False,
                "error": "Agent failed to run.",
                "agent": agent_name,
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result

    except Exception as e:
        logging.debug(
            f"Switching from agent: '{agent_name}' with error: {e.__class__.__name__}('{e}')"
        )
        return {"success": False, "error": str(e), "agent": agent_name}


@tool(tool_name="call_agent")
def call_agent_memory_handoff(
    action_context: ActionContext, agent_name: str, task: str
) -> dict:
    """
    Invoke another agent to perform a specific task using the `Memory Handoff: Continuing the Conversation` pattern
    where the second agent picks up where the first agent left off, with full context of what’s happened so far.
    All agents share and update the same `Memory` object.

    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform

    Returns:
        The result from the invoked agent's final memory
    """
    logging.debug(f"Switching to agent: '{agent_name}' for the task: '{task}'")

    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        error_message = f"No agent registry found in context!"
        logging.error(error_message)
        raise ValueError(error_message)

    # Get the agent's run function from the registry
    agent = agent_registry.get_agent(agent_name)
    if not agent:
        error_message = f"Agent '{agent_name}' not found in registry: {" ".join(agent_registry.get_agent_descriptions())}"
        logging.error(error_message)
        raise ValueError(error_message)

    logging.debug(f"Handing over to '{agent.name}': '{agent.description}'")

    invoked_memory = action_context.get_memory()

    try:
        # Run the agent with the provided task
        result_memory = agent.run(
            user_input=task,
            memory=invoked_memory,
        )

        # Get the last memory item as the result
        if result_memory.items:
            last_memory = result_memory.items[-1]
            result = {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content"),
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result
        else:
            result = {
                "success": False,
                "error": "Agent failed to run.",
                "agent": agent_name,
            }
            logging.debug(f"Switching from agent: '{agent_name}' with result: {result}")
            return result

    except Exception as e:
        logging.debug(
            f"Switching from agent: '{agent_name}' with error: {e.__class__.__name__}('{e}')"
        )
        return {"success": False, "error": str(e), "agent": agent_name}
