"""Concrete game state implementations."""

from __future__ import annotations

import pygame

from menus import pause_menu
from rendering import draw_player_sprite
from settings import MINUTES_PER_FRAME
from state_manager import GameState


class PlayState(GameState):
    """Normal gameplay state."""

    def __init__(self, game) -> None:
        self.game = game

    def on_enter(self) -> None:  # pragma: no cover - nothing special on enter
        pass

    def on_exit(self) -> None:  # pragma: no cover - nothing special on exit
        pass

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.state_manager.change_state(PauseState(self.game))

    def update(self) -> None:
        self.game.frame += 1
        self.game.player.time = (self.game.player.time + MINUTES_PER_FRAME) % 1440

    def render(self, screen) -> None:
        screen.fill((0, 0, 0))
        draw_player_sprite(screen, self.game.player.rect, frame=self.game.frame)
        pygame.display.flip()


class PauseState(GameState):
    """Temporary state that shows the pause menu."""

    def __init__(self, game) -> None:
        self.game = game

    def on_enter(self) -> None:
        # The pause menu is blocking; once it returns we go back to the play state
        self.game.player = pause_menu(self.game, self.game.player)
        self.game.state_manager.change_state(PlayState(self.game))

    def on_exit(self) -> None:  # pragma: no cover - nothing to clean up
        pass

    def handle_events(self, events) -> None:  # pragma: no cover - never called
        pass

    def update(self) -> None:  # pragma: no cover - never called
        pass

    def render(self, screen) -> None:  # pragma: no cover - never called
        pass
