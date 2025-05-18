"""A basic time-aware agent with chat capability using Ollama"""

import game.language as language
from game.action.library.default import get_current_date_and_time, terminate, user_input
from game.agent import Agent
from game.goal import Goal
from game.llm.litellm_completion import LiteLlm
from game.utils.memory import print_memory

if __name__ == "__main__":
    agent = Agent(
        name="chat_agent",
        description="Agent that chats with user",
        llm=LiteLlm(model="ollama/gemma3:12b", base_url="http://localhost:11434"),
        agent_language=language.AgentJsonActionLanguage(),
        tools=[user_input, get_current_date_and_time, terminate],
        goals=[
            Goal(
                priority=1,
                name="Ask user questions",
                description="You are a useful AI assistant that chats with user and responds to their questions. "
                "Always respond back to the user using a tool call. ",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when user requests to exit and provide a summary of the discussion",
            ),
        ],
    )

    memory = agent.run("Hi!", action_context_props={"time_zone": "Europe/Berlin"})

    print_memory(memory)
