"""Menu screens split from game.py."""

from __future__ import annotations

import json
import os
import sys
import pygame

from helpers import recalc_layouts, compute_slot_rects, scaled_font
from quests import LEADERBOARD_FILE
import settings
from inventory import crafting_exp_needed


def _binding_name(code: int) -> str:
    return pygame.key.name(code) if code >= 0 else f"Button {-code-1}"


def controls_menu(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Allow the player to remap key bindings."""
    actions = list(settings.KEY_BINDINGS.keys())
    idx = 0

    def save() -> None:
        os.makedirs(os.path.dirname(settings.KEY_BINDINGS_FILE), exist_ok=True)
        with open(settings.KEY_BINDINGS_FILE, "w") as f:
            json.dump(settings.KEY_BINDINGS, f)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save()
                    return
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(actions)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(actions)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    waiting = True
                    while waiting:
                        for ev in pygame.event.get():
                            if ev.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if ev.type == pygame.KEYDOWN:
                                settings.KEY_BINDINGS[actions[idx]] = [ev.key]
                                save()
                                waiting = False
                            elif ev.type == pygame.JOYBUTTONDOWN:
                                settings.KEY_BINDINGS[actions[idx]] = [-(ev.button + 1)]
                                save()
                                waiting = False
                        screen.fill((0, 0, 0))
                        prompt = font.render(
                            "Press a key or button...", True, (255, 255, 255)
                        )
                        screen.blit(
                            prompt,
                            (
                                settings.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                                settings.SCREEN_HEIGHT // 2 - prompt.get_height() // 2,
                            ),
                        )
                        pygame.display.flip()
                        pygame.time.wait(20)
        screen.fill((0, 0, 0))
        title = font.render("Controls", True, (255, 255, 255))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        for i, action in enumerate(actions):
            binds = ", ".join(_binding_name(b) for b in settings.KEY_BINDINGS[action])
            color = (255, 255, 0) if i == idx else (200, 200, 200)
            txt = font.render(f"{action}: {binds}", True, color)
            screen.blit(txt, (100, 120 + i * 40))
        info = font.render("Enter to rebind, Esc to exit", True, (200, 200, 200))
        screen.blit(info, (100, settings.SCREEN_HEIGHT - 80))
        pygame.display.flip()
        pygame.time.wait(20)


def start_menu(screen: pygame.Surface, font: pygame.font.Font) -> bool:
    """Display the start menu. Returns True if load was chosen."""
    board = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            try:
                board = json.load(f)
            except Exception:
                board = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                recalc_layouts()
                slot_rects = compute_slot_rects()
                font = scaled_font(28)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return False
                if event.key == pygame.K_l:
                    return True
                if event.key == pygame.K_c:
                    controls_menu(screen, font)
        screen.fill((0, 0, 0))
        title = font.render("Stick RPG Clone", True, (255, 255, 255))
        start_txt = font.render("Press Enter to Start", True, (230, 230, 230))
        load_txt = font.render("Press L to Load Game", True, (230, 230, 230))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 260))
        screen.blit(
            start_txt, (settings.SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 320)
        )
        screen.blit(
            load_txt, (settings.SCREEN_WIDTH // 2 - load_txt.get_width() // 2, 360)
        )
        controls_txt = font.render("Press C for Controls", True, (230, 230, 230))
        screen.blit(
            controls_txt,
            (settings.SCREEN_WIDTH // 2 - controls_txt.get_width() // 2, 400),
        )
        if board:
            lb_title = font.render("Top Completions", True, (230, 230, 230))
            screen.blit(
                lb_title, (settings.SCREEN_WIDTH // 2 - lb_title.get_width() // 2, 440)
            )
            for i, rec in enumerate(board):
                txt = font.render(
                    f"{i+1}. Day {rec['day']} - ${rec['money']}", True, (200, 200, 200)
                )
                screen.blit(
                    txt,
                    (settings.SCREEN_WIDTH // 2 - txt.get_width() // 2, 460 + i * 20),
                )
        pygame.display.flip()
        pygame.time.wait(20)


def draw_workshop_menu(surface: pygame.Surface, font: pygame.font.Font, player, recipes):
    """Render the crafting recipe list inside the workshop."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 120, settings.SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Workshop", True, settings.FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    y = 120
    if player.crafting_skills:
        for skill, lvl in player.crafting_skills.items():
            xp = player.crafting_exp.get(skill, 0)
            needed = crafting_exp_needed(player, skill)
            prog = font.render(
                f"{skill.title()} Lv{lvl} {xp}/{needed}",
                True,
                settings.FONT_COLOR,
            )
            surface.blit(prog, (100, y))
            y += 40
    else:
        txt = font.render("No crafting skills", True, settings.FONT_COLOR)
        surface.blit(txt, (100, y))
        y += 40

    if not player.known_recipes:
        txt = font.render("No recipes known", True, settings.FONT_COLOR)
        surface.blit(txt, (100, y))
    else:
        for i, name in enumerate(player.known_recipes):
            recipe = recipes.get(name, {})
            reqs = ", ".join(
                f"{amt} {res}" for res, amt in recipe.get("requires", {}).items()
            )
            skill = recipe.get("skill", "crafting").title()
            lvl = recipe.get("level", 1)
            line = font.render(
                f"{i+1}: {name} ({skill} Lv{lvl}) - {reqs}",
                True,
                settings.FONT_COLOR,
            )
            surface.blit(line, (100, y + i * 40))

    info_y = y + len(player.known_recipes) * 40 + 20
    info = font.render("[Q] Exit  [R] Repair", True, settings.FONT_COLOR)
    surface.blit(info, (100, info_y))


def character_creation(screen: pygame.Surface, font: pygame.font.Font):
    """Prompt for name and colors."""
    name = ""
    colors = [(40, 40, 40), (200, 50, 50), (50, 90, 200)]
    color_names = ["Black", "Red", "Blue"]
    head_colors = [(245, 219, 164), (224, 188, 135), (192, 152, 109)]
    head_color_names = ["Light", "Tan", "Brown"]
    body_idx = 0
    head_idx = 0
    selecting_head = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return (name or "Player"), colors[body_idx], head_colors[head_idx]
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_TAB:
                    selecting_head = not selecting_head
                elif event.key == pygame.K_LEFT:
                    if selecting_head:
                        head_idx = (head_idx - 1) % len(head_colors)
                    else:
                        body_idx = (body_idx - 1) % len(colors)
                elif event.key == pygame.K_RIGHT:
                    if selecting_head:
                        head_idx = (head_idx + 1) % len(head_colors)
                    else:
                        body_idx = (body_idx + 1) % len(colors)
                elif event.unicode and event.unicode.isprintable() and len(name) < 12:
                    name += event.unicode
        screen.fill((0, 0, 0))
        title = font.render("Create Character", True, (255, 255, 255))
        prompt = font.render(f"Name: {name}", True, (230, 230, 230))
        body_txt = font.render(
            f"Body Color: {color_names[body_idx]} (\u2190/\u2192)",
            True,
            colors[body_idx],
        )
        head_txt = font.render(
            f"Head Color: {head_color_names[head_idx]} (\u2190/\u2192)",
            True,
            head_colors[head_idx],
        )
        toggle_txt = font.render("Press TAB to switch", True, (230, 230, 230))
        confirm = font.render("Press Enter to Start", True, (230, 230, 230))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 240))
        screen.blit(prompt, (settings.SCREEN_WIDTH // 2 - prompt.get_width() // 2, 280))
        screen.blit(
            body_txt, (settings.SCREEN_WIDTH // 2 - body_txt.get_width() // 2, 320)
        )
        screen.blit(
            head_txt, (settings.SCREEN_WIDTH // 2 - head_txt.get_width() // 2, 350)
        )
        screen.blit(
            toggle_txt, (settings.SCREEN_WIDTH // 2 - toggle_txt.get_width() // 2, 380)
        )
        screen.blit(
            confirm, (settings.SCREEN_WIDTH // 2 - confirm.get_width() // 2, 410)
        )
        pygame.display.flip()
        pygame.time.wait(20)
