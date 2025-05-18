from typing import Optional

from game.action import Action


class ActionRegistry:

    def __init__(self):
        self.actions = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(<ACTIONS: {list(self.actions)}>)"

    def register(self, action: Action):
        self.actions[action.name] = action

    def get_action(self, name: str) -> Optional[Action]:
        return self.actions.get(name, None)

    def get_actions(self) -> list[Action]:
        """Get all registered actions"""
        return list(self.actions.values())
