"""
Multi-agent example using a:
 - Chat agent whose purpose is to chat with the user

"""

import game.action.library.multi_agent as multi_agent
import game.language as language
from game.action.library.default import get_current_date_and_time, terminate, user_input
from game.agent import Agent
from game.goal import Goal
from game.utils.memory import print_memory


def get_chat_agent(agent_language: language.AgentLanguage) -> Agent:
    return Agent(
        name="chat_agent",
        description="Agent that chats with user",
        agent_language=agent_language,
        tools=[user_input, get_current_date_and_time, terminate],
        goals=[
            Goal(
                priority=1,
                name="Ask user questions",
                description="You are a useful AI assistant that chats with user and responds to their questions. "
                "Always respond back to the user using a tool call."
                "The user can only see what you send with the tool call",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when user requests to exit and provide a message of what the user needs",
            ),
        ],
    )


if __name__ == "__main__":
    # l = language.AgentJsonActionLanguage()
    l = language.AgentFunctionCallingActionLanguage()

    chat_agent = get_chat_agent(l)
    manager_agent = Agent(
        name="manager_agent",
        description="Manages and delegates tasks to agents",
        managed_agents=[chat_agent],
        agent_language=l,
        multi_agents_memory_model=multi_agent.call_agent_memory_handoff,
        goals=[
            Goal(
                priority=1,
                name="Manage Agents",
                description="You are an AI Agent Manager that manages a list of AI Agents with specific capabilities. "
                "Your goal is to delegate tasks to them that match their capabilities. "
                "When you delegate a task to an agent, always provide an appropriate task description. ",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when done and provide a summary of the user's requests and agent findings as the message parameter",
            ),
        ],
    )

    memory = manager_agent.run("Hi, I have a question")
    print_memory(memory, info=manager_agent.name)
