"""Simple state management for game screens."""

from __future__ import annotations

from typing import Optional


class GameState:
    """Base class for individual game states."""

    def on_enter(self) -> None:  # pragma: no cover - default implementation
        pass

    def on_exit(self) -> None:  # pragma: no cover - default implementation
        pass

    def handle_events(self, events) -> None:  # pragma: no cover - default implementation
        pass

    def update(self) -> None:  # pragma: no cover - default implementation
        pass

    def render(self, screen) -> None:  # pragma: no cover - default implementation
        pass


class StateManager:
    """Maintain and delegate to the active :class:`GameState`."""

    def __init__(self) -> None:
        self.state: Optional[GameState] = None

    def change_state(self, new_state: GameState) -> None:
        if self.state:
            self.state.on_exit()
        self.state = new_state
        self.state.on_enter()

    def handle_events(self, events) -> None:
        if self.state:
            self.state.handle_events(events)

    def update(self) -> None:
        if self.state:
            self.state.update()

    def render(self, screen) -> None:
        if self.state:
            self.state.render(screen)
