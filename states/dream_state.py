"""Dream gameplay state handling visualization and dream resolution."""

from __future__ import annotations

import random
from typing import Dict, Tuple, List, Any

import pygame

from . import PlayState
from inventory import dream_shop_purchase


class DreamState(PlayState):
    """Temporary state that shows a dream sequence before returning to play."""

    def __init__(self, game, event: Dict[str, object]) -> None:
        super().__init__(game)
        self.event = event
        self.duration: int = int(event.get("duration", 180))
        self.elapsed = 0
        self.finished = False
        inventory = event.get("shop_inventory")
        self.shop_inventory: List[Dict[str, Any]] = inventory if isinstance(inventory, list) else []
        self.message: str = ""
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
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self._return_to_play()
                elif self.shop_inventory and pygame.K_1 <= event.key <= pygame.K_9:
                    index = event.key - pygame.K_1
                    self._attempt_purchase(index)
                elif self.shop_inventory and event.key == pygame.K_0:
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
                self.event.get("flavor", ""),
                "",
                self.event.get("summary", ""),
            ]
            self._draw_centered_lines(screen, lines, font)
            if self.shop_inventory:
                self._draw_shop(screen, font)
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

    def _draw_shop(self, screen, font) -> None:
        base_x = int(screen.get_width() * 0.1)
        base_y = int(screen.get_height() * 0.6)
        line_height = font.get_height() + 6
        shards_text = font.render(
            f"Dream Shards: {self.game.player.dream_shards}", True, (255, 255, 200)
        )
        screen.blit(shards_text, (base_x, base_y))
        base_y += line_height
        for idx, offer in enumerate(self.shop_inventory):
            name = str(offer.get("name", "Mystery"))
            cost = int(offer.get("cost", 0))
            purchased = offer.get("purchased", False)
            status = " - Sold" if purchased else ""
            label = f"{idx + 1}. {name} - {cost} shards{status}"
            if purchased:
                color = (120, 120, 120)
            elif self.game.player.dream_shards < cost:
                color = (220, 140, 140)
            else:
                color = (220, 220, 255)
            screen.blit(font.render(label, True, color), (base_x, base_y))
            base_y += line_height
        instructions = "Press 1-9 to buy, Enter to wake"
        screen.blit(font.render(instructions, True, (255, 255, 255)), (base_x, base_y))
        if self.message:
            base_y += line_height
            screen.blit(font.render(self.message, True, (255, 230, 160)), (base_x, base_y))

    def _attempt_purchase(self, index: int) -> None:
        if not self.shop_inventory:
            return
        self.message = dream_shop_purchase(self.game.player, self.shop_inventory, index)

    def _return_to_play(self) -> None:
        if not self.finished:
            self.finished = True
            self.game.state_manager.change_state(PlayState(self.game))
