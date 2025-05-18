"""G - Goals Implementation

Goals will describe what we are trying to achieve and how to achieve it. By encapsulating them into objects, we can move away from large “walls of text” that represent the instructions for our agent. Additionally, we can add priority to our goals, which will help us decide which goal to pursue first and how to sort or format them when combining them into a prompt.

We broadly use the term “goal” to encompass both “what” the agent is trying to achieve and “how” it should approach the task. This duality is crucial for guiding the agent’s behavior effectively. An important type of goal can be examples that show the agent how to reason in certain situations. We can also build goals that define core rules that are common across all agents in our system or that give it special instructions on how to solve certain types of tasks

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/3d8su/modular-ai-agent-design
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Goal:
    priority: int
    name: str
    description: str

    def to_dict(self) -> dict:
        return asdict(self)
