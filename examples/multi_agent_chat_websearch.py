"""
Multi-agent example using a:
 - Chat agent whose purpose is to figure out what a user want
 - Web search agent whose purpose is to search internet and webpages
"""

import re

import requests
from markdownify import markdownify
from requests.exceptions import RequestException

import game.action.library.multi_agent as agent_communication
import game.language as language
from game.action import tool
from game.action.library.default import get_current_date_and_time, terminate, user_input
from game.agent import Agent
from game.goal import Goal
from game.utils.memory import print_memory


@tool()
def web_search(query: str) -> str:
    """
    Performs a web search for a query and returns a string of the top search results formatted as markdown with titles, links, and descriptions.
    Args:
        query: The search query to perform.

    Returns:

    """
    # https://github.com/huggingface/smolagents/blob/v1.15.0/src/smolagents/default_tools.py#L213

    def _create_duckduckgo_parser():
        from html.parser import HTMLParser

        class SimpleResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self.current = {}
                self.capture_title = False
                self.capture_description = False
                self.capture_link = False

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "a" and attrs.get("class") == "result-link":
                    self.capture_title = True
                elif tag == "td" and attrs.get("class") == "result-snippet":
                    self.capture_description = True
                elif tag == "span" and attrs.get("class") == "link-text":
                    self.capture_link = True

            def handle_endtag(self, tag):
                if tag == "a" and self.capture_title:
                    self.capture_title = False
                elif tag == "td" and self.capture_description:
                    self.capture_description = False
                elif tag == "span" and self.capture_link:
                    self.capture_link = False
                elif tag == "tr":
                    # Store current result if all parts are present
                    if {"title", "description", "link"} <= self.current.keys():
                        self.current["description"] = " ".join(
                            self.current["description"]
                        )
                        self.results.append(self.current)
                        self.current = {}

            def handle_data(self, data):
                if self.capture_title:
                    self.current["title"] = data.strip()
                elif self.capture_description:
                    self.current.setdefault("description", [])
                    self.current["description"].append(data.strip())
                elif self.capture_link:
                    self.current["link"] = "https://" + data.strip()

        return SimpleResultParser()

    response = requests.get(
        "https://lite.duckduckgo.com/lite/",
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    parser = _create_duckduckgo_parser()
    parser.feed(response.text)
    results = parser.results
    if len(results) == 0:
        return "No results found! Try a less restrictive/shorter query."

    return "## Search Results\n\n" + "\n\n".join(
        [
            f"[{result['title']}]({result['link']})\n{result['description']}"
            for result in results
        ]
    )


@tool()
def visit_webpage(url: str) -> str:
    """Visits a webpage at the given URL and returns its content as a markdown string.

    Args:
        url: The URL of the webpage to visit.

    Returns:
        The content of the webpage converted to Markdown, or an error message if the request fails.
    """
    # https://huggingface.co/docs/smolagents/en/examples/multiagents
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Convert the HTML content to Markdown
        markdown_content = markdownify(response.text).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

        return markdown_content

    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def get_chat_agent(agent_language: language.AgentLanguage) -> Agent:
    """Instantiates a chat agent"""
    return Agent(
        name="chat_agent",
        description="Agent that chats with user and tries to figure out what the user needs.",
        agent_language=agent_language,
        tools=[user_input, get_current_date_and_time, terminate],
        goals=[
            Goal(
                priority=1,
                name="Ask user questions",
                description="You are a useful AI assistant. Your goal is to chat with the user and understand what they need. "
                "Terminate the chat as soon as you figure out what the user needs. "
                "Always respond back to the user using a tool call. "
                "The user can only see what you send with the tool call.",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when you know what the user wants and provide the user's needs in the message",
            ),
        ],
    )


def get_web_agent(agent_language: language.AgentLanguage) -> Agent:
    """Instantiates a web search/visiting AI agent"""
    return Agent(
        name="web_search_agent",
        description="Agent that runs web searches and visits websites for you.",
        agent_language=agent_language,
        tools=[web_search, visit_webpage, terminate],
        goals=[
            Goal(
                priority=1,
                name="Gather Information",
                description="You are a useful AI assistant that runs web searches to find information based on the user's needs. and can also visit websites",
            ),
            Goal(
                priority=2,
                name="Terminate",
                description="Call terminate when done and provide a summary of your findings in the message parameter",
            ),
        ],
    )


if __name__ == "__main__":
    l = language.AgentFunctionCallingActionLanguage()

    manager_agent = Agent(
        name="manager_agent",
        description="Manages and delegates tasks to agents",
        managed_agents=[get_web_agent(l), get_chat_agent(l)],
        agent_language=l,
        multi_agents_memory_model=agent_communication.call_agent_message_passing,
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
