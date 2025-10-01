"""Concrete game state implementations."""

from __future__ import annotations

import pygame

from menus import pause_menu, business_menu, shop_menu
from rendering import draw_player_sprite, draw_npc
from settings import MINUTES_PER_FRAME
import settings

from menus import pause_menu, business_menu, pet_shop_menu
from rendering import (
    draw_player_sprite,
    draw_npc,
    draw_building,
    draw_road_and_sidewalks,
    draw_city_walls,
    draw_decorations,
    draw_day_night,
    draw_weather,
    draw_sky,
    draw_ui,
    draw_quest_marker,
)
from settings import MINUTES_PER_FRAME, SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, KEY_BINDINGS
from helpers import quest_target_building

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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for b in self.game.buildings:
                    if b.rect.colliderect(self.game.player.rect):
                        if b.btype == "business":
                            business_menu(self.game, self.game.player)
                        elif b.btype == "shop":
                            shop_menu(self.game, self.game.player)

                        elif b.btype == "townhall":
                            # Progress story when visiting Town Hall
                            from quests import check_story, choose_story_branch

                            if self.game.player.story_stage == 0:
                                self.game.player.story_stage = 1
                                check_story(self.game.player)
                                if self.game.sound_enabled and self.game.enter_sound:
                                    try:
                                        self.game.enter_sound.play()
                                    except Exception:
                                        pass
                            elif self.game.player.story_stage == 1 and not self.game.player.story_branch:
                                # Default to mayor branch on confirm; simple progression
                                choose_story_branch(self.game.player, "mayor")
                                check_story(self.game.player)
                                if self.game.sound_enabled and self.game.enter_sound:
                                    try:
                                        self.game.enter_sound.play()
                                    except Exception:
                                        pass
                        elif b.btype == "petshop":
                            pet_shop_menu(self.game, self.game.player)
                        break

    def update(self) -> None:
        self.game.frame += 1
        keys = pygame.key.get_pressed()
        speed = settings.PLAYER_SPEED
        if any(keys[k] for k in KEY_BINDINGS.get("run", [])) and getattr(
            self.game.player, "has_skateboard", False
        ):
            speed = int(speed * settings.SKATEBOARD_SPEED_MULT)

        dx = dy = 0
        if any(keys[k] for k in KEY_BINDINGS.get("move_left", [])):
            dx -= speed
            self.game.player.facing_left = True
        if any(keys[k] for k in KEY_BINDINGS.get("move_right", [])):
            dx += speed
            self.game.player.facing_left = False
        if any(keys[k] for k in KEY_BINDINGS.get("move_up", [])):
            dy -= speed
        if any(keys[k] for k in KEY_BINDINGS.get("move_down", [])):
            dy += speed

        if dx or dy:
            self.game.player.rect.x = max(0, min(MAP_WIDTH - self.game.player.rect.width, self.game.player.rect.x + dx))
            self.game.player.rect.y = max(0, min(MAP_HEIGHT - self.game.player.rect.height, self.game.player.rect.y + dy))
            if self.game.sound_enabled and self.game.step_sound:
                # Play a very soft step sound sparingly
                if self.game.frame % 12 == 0:
                    try:
                        self.game.step_sound.play()
                    except Exception:
                        pass

        # advance world time
        self.game.player.time = (self.game.player.time + MINUTES_PER_FRAME) % 1440

        # update NPCs
        update_npcs(
            self.game.player,
            self.game.npcs,
            self.game.buildings,
            self.game.tilemap,
        )

    def render(self, screen) -> None:
        player = self.game.player
        # Camera follows player horizontally
        cam_x = max(0, min(MAP_WIDTH - SCREEN_WIDTH, player.rect.centerx - SCREEN_WIDTH // 2))
        cam_y = 0

        # Sky and ground
        draw_sky(screen, player.time)
        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_decorations(screen, cam_x, cam_y)

        # Buildings
        target = quest_target_building(player, self.game.buildings)
        for b in self.game.buildings:
            highlight = b is target or b.rect.colliderect(player.rect.inflate(12, 12))
            # draw with camera offset by blitting to a temp surface via position adjustment
            # draw_building expects world coordinates already on screen, so shift a subsurface
            # Instead, temporarily shift rect during draw
            original = b.rect
            b.rect = pygame.Rect(b.rect.x - cam_x, b.rect.y - cam_y, b.rect.width, b.rect.height)
            draw_building(screen, b, highlight=highlight, cam_x=cam_x, player=player, frame=self.game.frame)
            b.rect = original

        # Player and NPCs
        for npc in self.game.npcs:
            draw_npc(screen, npc, self.game.font, offset=(-cam_x, -cam_y))
        pr = player.rect.move(-cam_x, -cam_y)
        draw_player_sprite(
            screen,
            pr,
            frame=self.game.frame,
            facing_left=player.facing_left,
            color=player.color,
            head_color=player.head_color,
            pants_color=player.pants_color,
            has_hat=player.has_hat,
            hat_color=player.hat_color,
        )

        # Night overlay and weather
        night_alpha = draw_day_night(screen, player.time)
        draw_weather(screen, player.weather)

        # Quest arrow and UI
        if target:
            draw_quest_marker(screen, pr, target.rect, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)
        from quests import QUESTS, STORY_QUESTS

        draw_ui(screen, self.game.font, player, QUESTS, STORY_QUESTS)
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


from .dream_state import DreamState  # noqa: E402

__all__ = ["PlayState", "PauseState", "DreamState", "update_npcs"]
