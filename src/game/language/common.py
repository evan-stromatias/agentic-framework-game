from typing import Optional

from game.goal import Goal


def format_goals(goals: list[Goal]) -> str:
    """Maps all goals int a single string that concatenates their description"""
    sep = "\n-------------------\n"
    return "\n\n".join([f"{goal.name}:{sep}{goal.description}{sep}" for goal in goals])


def format_managed_agents(
    managed_agent_descriptions: Optional[list[dict[str, str]]] = None,
) -> str:
    """
    :param managed_agent_descriptions: List of `agent: description`s for multi-agent systems.
    """
    available_managed_agents_str = ""
    descriptions = []
    if managed_agent_descriptions:
        for agent_description in managed_agent_descriptions:
            for agent_name, description in agent_description.items():
                descriptions.append(f"{agent_name}:\n\t{description}")
        available_managed_agents_str = (
            "\n".join([f"- {m}" for m in managed_agent_descriptions])
            if managed_agent_descriptions
            else ""
        )
        available_managed_agents_str = (
            f"\nAvailable Agents: \n{available_managed_agents_str}\n"
        )
    return available_managed_agents_str
