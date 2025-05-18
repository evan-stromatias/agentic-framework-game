# 🧠 agentic-framework-game

GAME is an agentic AI framework that exists purely for educational purposes. 

It was created while I was following the [AI Agents and Agentic AI in Python: Powered by Generative AI Specialization](https://www.coursera.org/specializations/ai-agents-python)
specialization by [Dr. Jules White](https://www.coursera.org/instructor/juleswhite). 
The courses provided small code snippets, so I initially created this repository to follow along the course.
Later I used this repo as a sandbox to learn and experiment with various agentic concepts, so it's not 100% identical 
to the courses. 

The **GAME** framework provides a structured way to design AI agents, ensuring modularity and adaptability. 
It breaks agent design into four essential components:

- **G - Goals / Instructions**: What the agent is trying to accomplish and its instructions on how to try to achieve its goals.
- **A - Actions**: The tools the agent can use to achieve its goals.
- **M - Memory**: How the agent retains information across interactions, which determines what information it will have available in each iteration of the agent loop.
- **E - Environment**: The agent’s interface to the external world where it executes actions and gets feedback on the results of those actions.

## 🗼  Core Components

*   **Agent:** The main class that orchestrates the agent loop, constructing prompts, executing actions, and managing memory.
*   **Goal:** Represents what the agent aims to achieve, with a priority assigned to each goal.
*   **Action:** Defines a discrete capability that the agent can execute in the environment.
*   **Memory:** Stores the agent's interactions and experiences.
*   **Environment:** Executes actions and returns results to the agent.
*   **Language:** Translates between the agent's internal representation and the LLM's input/output format (e.g., JSON, function calling).
*   **LLM:** An abstraction for interacting with language models.
*   **Tool:** Represents a function that the agent can use to interact with the environment.

### 🔁 Agent Loop

The agent operates in a loop:

1.  **Construct Prompt:** The `AgentLanguage` transforms Goals, Actions, and Memory into a prompt for the LLM.
2.  **Generate Response:** The LLM generates a response based on the prompt.
3.  **Parse Response:** The `AgentLanguage` parses the LLM's response to determine the action to execute.
4.  **Execute Action:** The `Environment` executes the action.
5.  **Update Memory:** The agent's `Memory` is updated with the LLM's response and the result of the action.

## 🏗️ Project Structure
```
game/
├── src/
│   └── game/
│       ├── action/                             Defines the actions that agents can take within the game environment.
│       │   ├── action.py                       Contains the base `Action` class returned by the @tool decorator
│       │   ├── context.py                      Defines the `ActionContext` class, providing context for action execution
│       │   ├── python_registry.py              Registers python functions as actions
│       │   ├── registry.py                     Manages the registration of available actions
│       │   ├── tool_decorator.py               Decorator for creating tools (`Action` objects from functions)
│       │   ├── library/
│       │   │   ├── default.py                  Default tools like `terminate` or `get_user_input`
│       │   │   ├── multi_agent.py              Tools for multi-agent interactions and hand-overs
│       ├── language/                           Translates between the agent's internal representation and the LLM's input/output format (e.g., JSON, function calling)
│       │   ├── base.py                         Contains the base `LanguageModel` class
│       │   ├── exceptions.py                   Contains the exception classes raised by `LanguageModel`
│       │   ├── function_calling_language.py    Implements function calling with language models
│       │   ├── json_action_language.py
│       ├── llm/                                Defines the LLM models used by the agent
│       │   ├── base.py                         Contains the base `Llm` class
│       │   ├── litellm_completion.py           Implements language model completion using LiteLLM
│       ├── memory/                             Defines the memory systems used by the agents
│       │   ├── base.py                         Contains the base `Memory` class
│       │   ├── dict_memory.py                  Implements a dictionary-based memory
│       ├── agent.py                            Defines the `Agent` class, representing an AI agent
│       ├── environment.py
│       ├── goal.py                             Defines the `Goal` class, representing the goals that agents try to achieve
│       ├── prompt.py                           Defines the prompts used by the language models
│       ├── logger.py                           Defines the logger
│       ├── settings.py                         Defines project settings from env variables
```

## 🚀 Getting Started

### 👩🏻‍💻 Running a simple chat agent

Create a virtual environment:
```commandline
python3.12 -m venv .venv
source .venv/bin/activate
```

```commandline
pip install git+https://github.com/evan-stromatias/agentic-framework-game.git@v{Y}.{X}.{Z}#egg=game
```
Example chat agent with tool calling:

```python
"""A basic time-aware agent with chat capability"""

import game.language as language
from game.action.library.default import get_current_date_and_time, terminate, user_input
from game.agent import Agent
from game.goal import Goal
from game.utils.memory import print_memory

if __name__ == "__main__":
    agent = Agent(
        name="chat_agent",
        description="Agent that chats with user",
        agent_language=language.AgentFunctionCallingActionLanguage(),
        tools=[user_input, get_current_date_and_time, terminate],
        goals=[
            Goal(
                priority=1,
                name="Ask user questions",
                description="You are a useful AI assistant that chats with user and responds to their questions. "
                "Always respond back to the user using a tool call.",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when user requests to exit and provide a summary of the discussion.",
            ),
        ],
    )

    memory = agent.run("Hi!", action_context_props={"time_zone": "Europe/Berlin"})

    print_memory(memory)
```

The project uses Pydantic settings and environment variables for configuration. 
If the user doesn't provide an `Llm` object to the Agent's constructor then the `LiteLlm` is used and configured by 
env variables (or a `.env` file), eg:
*   `LLM_MODEL`: The name of the LLM model to use (e.g. `gemini/gemini-2.0-flash`).
*   `LLM_API_KEY`: The API key for the LLM provider.

Alternatively:
```python
    agent = Agent(
        name="chat_agent",
        description="Agent that chats with user",
        llm=LiteLlm(model="ollama/gemma3:12b", base_url="http://localhost:11434"),
        ...
```

More examples can be found in the [examples](./examples) directory.

### 👩🏻‍🏭 Development

```bash
git clone https://github.com/evan-stromatias/agentic-framework-game.git
cd agentic-framework-game
```
Create a virtual environment:
```commandline
python3.12 -m venv .venv
source .venv/bin/activate
```
Install with development dependencies:
```commandline
pip install -e .[dev]
```
Run the unit-tests:
```commandline
pytest 
```
Setup pre-commit:
```commandline
pre-commit install
pre-commit run --all-files
```

The `version.txt` and `CHANGELOG.md` are updated by the CI/CD pipeline whenever a PR has been successfully merged to
the main branch and a new `TAG` version of the library is released.
