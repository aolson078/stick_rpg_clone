"""Dream gameplay state handling visualization and dream resolution."""

from __future__ import annotations

import random
from typing import Dict, Tuple

import pygame

from . import PlayState


class DreamState(PlayState):
    """Temporary state that shows a dream sequence before returning to play."""

    def __init__(self, game, event: Dict[str, object]) -> None:
        super().__init__(game)
        self.event = event
        self.duration: int = int(event.get("duration", 180))
        self.elapsed = 0
        self.finished = False
        self._particles = [
            (
                random.random(),
                random.random(),
                random.randint(1, 4),
                random.uniform(0.05, 0.4),
            )
            for _ in range(40)
        ]

    def on_enter(self) -> None:
        self.elapsed = 0
        self.finished = False

    def handle_events(self, events) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE,
                pygame.K_ESCAPE,
            ):
                self._return_to_play()

    def update(self) -> None:
        if self.finished:
            return
        self.elapsed += 1
        if self.elapsed >= self.duration:
            self._return_to_play()

    def render(self, screen) -> None:
        width, height = screen.get_size()
        base_color: Tuple[int, int, int] = tuple(self.event.get("color", (25, 10, 60)))  # type: ignore[arg-type]
        screen.fill(base_color)

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        for norm_x, norm_y, radius, speed in self._particles:
            offset_x = (norm_x * width + speed * self.elapsed * width) % width
            offset_y = (norm_y * height + speed * self.elapsed * height) % height
            alpha = max(60, min(220, int(200 * abs(((self.elapsed * speed) % 1.0) - 0.5) * 2)))
            color = (
                min(255, base_color[0] + 100),
                min(255, base_color[1] + 80),
                min(255, base_color[2] + 120),
                alpha,
            )
            pygame.draw.circle(overlay, color, (int(offset_x), int(offset_y)), radius)
        screen.blit(overlay, (0, 0))

        font = self.game.font
        if font:
            lines = [
                self.event.get("title", "Dreamscape"),
                "",
                self.event.get("description", ""),
                "",
                self.event.get("summary", ""),
            ]
            self._draw_centered_lines(screen, lines, font)
        pygame.display.flip()

    def _draw_centered_lines(self, screen, lines, font) -> None:
        non_empty = [line for line in lines if line]
        if not non_empty:
            return
        spacing = 12
        rendered = [font.render(str(line), True, (255, 255, 255)) for line in non_empty]
        total_height = sum(s.get_height() for s in rendered) + spacing * (len(rendered) - 1)
        current_y = screen.get_height() // 2 - total_height // 2
        render_iter = iter(rendered)
        for line in lines:
            if not line:
                current_y += spacing // 2
                continue
            surface = next(render_iter)
            rect = surface.get_rect(center=(screen.get_width() // 2, current_y + surface.get_height() // 2))
            screen.blit(surface, rect)
            current_y += surface.get_height() + spacing

    def _return_to_play(self) -> None:
        if not self.finished:
            self.finished = True
            self.game.state_manager.change_state(PlayState(self.game))
