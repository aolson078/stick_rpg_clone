"""Menu screens split from game.py."""

from __future__ import annotations

import json
import os
import sys
import pygame

from helpers import recalc_layouts, compute_slot_rects
from quests import LEADERBOARD_FILE
import settings


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
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return False
                if event.key == pygame.K_l:
                    return True
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
        if board:
            lb_title = font.render("Top Completions", True, (230, 230, 230))
            screen.blit(
                lb_title, (settings.SCREEN_WIDTH // 2 - lb_title.get_width() // 2, 400)
            )
            for i, rec in enumerate(board):
                txt = font.render(
                    f"{i+1}. Day {rec['day']} - ${rec['money']}", True, (200, 200, 200)
                )
                screen.blit(
                    txt,
                    (settings.SCREEN_WIDTH // 2 - txt.get_width() // 2, 420 + i * 20),
                )
        pygame.display.flip()
        pygame.time.wait(20)


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
