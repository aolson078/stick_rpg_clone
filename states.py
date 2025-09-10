"""Concrete game state implementations."""

from __future__ import annotations

import pygame

from menus import pause_menu
from rendering import draw_player_sprite, draw_npc
from settings import MINUTES_PER_FRAME
from state_manager import GameState
from pathfinding import find_path
from entities import Player, NPC, Building
from tilemap import TileMap
from typing import List


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
        update_npcs(
            self.game.player,
            self.game.npcs,
            self.game.buildings,
            self.game.tilemap,
        )

    def render(self, screen) -> None:
        screen.fill((0, 0, 0))
        for npc in self.game.npcs:
            draw_npc(screen, npc, self.game.font)
        draw_player_sprite(screen, self.game.player.rect, frame=self.game.frame)
        pygame.display.flip()


def update_npcs(
    player: Player,
    npcs: List[NPC],
    buildings: List[Building],
    tile_map: TileMap,
) -> None:
    """Update NPC destinations and advance their movement."""
    hour = int(player.time) // 60
    for npc in npcs:
        target = npc.home
        if npc.work and npc.work_start <= hour < npc.work_end:
            target = npc.work
        building = next((b for b in buildings if b.btype == target), None)
        if building:
            dest = (
                building.rect.centerx - npc.rect.width // 2,
                building.rect.centery - npc.rect.height // 2,
            )
            if npc.destination != dest:
                npc.destination = dest
                npc.path = find_path(tile_map, npc.rect.topleft, dest)
        npc.move()
        if npc.bubble_timer > 0:
            npc.bubble_timer -= 1
        if npc.rect.colliderect(player.rect.inflate(40, 40)):
            npc.bubble_message = f"Hi {player.name}"
            npc.bubble_timer = 60


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
