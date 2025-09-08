"""Main game loop and event handling encapsulated in a class."""

from __future__ import annotations

import pygame

import settings
from entities import Player
from helpers import recalc_layouts, scaled_font, load_game
from loaders import load_buildings
from menus import start_menu, character_creation
from settings import (
    MAP_HEIGHT,
    MAP_WIDTH,
    PLAYER_SIZE,
    MUSIC_FILE,
    STEP_SOUND_FILE,
    ENTER_SOUND_FILE,
    QUEST_SOUND_FILE,
    MUSIC_VOLUME,
    SFX_VOLUME,
)
from state_manager import StateManager
from states import PlayState


class Game:
    """Container for the running game state and main loop."""

    def __init__(self) -> None:
        # --- Pygame setup -------------------------------------------------
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        recalc_layouts()

        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except pygame.error:
            self.sound_enabled = False

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        # Basic resources
        self.clock = pygame.time.Clock()
        self.font = scaled_font(28)
        self.buildings = load_buildings()

        # Load audio assets if possible
        self.step_sound = self.enter_sound = self.quest_sound = None
        if self.sound_enabled:
            self.step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
            self.enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
            self.quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
            for snd in (self.step_sound, self.enter_sound, self.quest_sound):
                snd.set_volume(SFX_VOLUME)
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except pygame.error:
                # Music is optional; failing to load should not crash
                pass

        # --- Player setup ------------------------------------------------
        load_existing = start_menu(self)
        if load_existing:
            loaded = load_game()
        else:
            loaded = None
        if loaded:
            self.player = loaded
        else:
            name, color, head_color, pants_color, has_hat, hat_color = character_creation(
                self
            )
            self.player = Player(
                pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE),
                name=name,
                color=color,
                head_color=head_color,
                pants_color=pants_color,
                has_hat=has_hat,
                hat_color=hat_color,
            )

        self.running = True
        self.frame = 0

        # Initialize state manager with the default gameplay state
        self.state_manager = StateManager()
        self.state_manager.change_state(PlayState(self))

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Run the main game loop."""
        while self.running:
            events = pygame.event.get()
            self.state_manager.handle_events(events)
            self.state_manager.update()
            self.state_manager.render(self.screen)
            self.clock.tick(60)


def main() -> None:
    """Entry point used by tests or scripts."""
    Game().run()


if __name__ == "__main__":
    main()

