"""Menu screens split from game.py."""

from __future__ import annotations

import json
import os
import sys
from typing import TYPE_CHECKING, Dict

import pygame

from helpers import recalc_layouts, compute_slot_rects, scaled_font, save_game, load_game
from businesses import (
    manage_business,
    hire_staff,
    run_marketing_campaign,
    schedule_future_contract,
    train_staff,
    cash_out_future,
)
from quests import LEADERBOARD_FILE
import settings
from inventory import (
    SHOP_ITEMS,
    buy_shop_item,
    crafting_exp_needed,
    duplicate_card_rarity_counts,
    get_shop_price,
)

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from game import Game


def _binding_name(code: int) -> str:
    return pygame.key.name(code) if code >= 0 else f"Button {-code-1}"


def controls_menu(
    game: "Game", screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
) -> None:
    """Allow the player to remap key bindings.

    The menu normally uses the screen and font stored on the provided
    :class:`~game.Game` instance.  ``screen`` and ``font`` parameters are kept
    for backward compatibility and ease of testing.
    """
    screen = screen or game.screen
    font = font or game.font
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


def deck_build_menu(
    game: "Game", player, screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
) -> None:
    """Simple deck building interface to assemble up to 30 cards.

    Uses arrow keys to navigate the player's card collection and Enter to add
    cards to the active deck.  Backspace removes the last added card.  Esc exits
    the menu saving the current deck selection.
    """

    screen = screen or game.screen
    font = font or game.font
    available = player.cards
    deck = list(player.deck)
    idx = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    player.deck = deck
                    return
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(available) if available else 0
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(available) if available else 0
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if len(deck) < 30 and available:
                        deck.append(available[idx])
                elif event.key == pygame.K_BACKSPACE and deck:
                    deck.pop()

        screen.fill((0, 0, 0))
        title = font.render("Deck Builder", True, (255, 255, 255))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        for i, name in enumerate(available):
            color = (255, 255, 0) if i == idx else (200, 200, 200)
            txt = font.render(name, True, color)
            screen.blit(txt, (100, 120 + i * 30))
        deck_txt = font.render(f"Deck: {len(deck)}/30", True, (200, 200, 200))
        screen.blit(deck_txt, (settings.SCREEN_WIDTH - deck_txt.get_width() - 20, 80))
        pygame.display.flip()
        pygame.time.wait(20)


def _format_card_requirements(card_cost: Dict[str, int]) -> str:
    parts = [f"{rarity.title()} x{amount}" for rarity, amount in sorted(card_cost.items())]
    return ", ".join(parts) if parts else ""


def _format_duplicate_summary(duplicates: Dict[str, int]) -> str:
    if not duplicates:
        return "None"
    return ", ".join(f"{rarity.title()} x{count}" for rarity, count in sorted(duplicates.items()))


def shop_menu(
    game: "Game",
    player,
    screen: pygame.Surface | None = None,
    font: pygame.font.Font | None = None,
) -> None:
    """Display the general store inventory and allow purchases."""

    screen = screen or game.screen
    font = font or game.font

    if not SHOP_ITEMS:
        return

    idx = 0
    payment_mode = "cash"
    message = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(SHOP_ITEMS)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(SHOP_ITEMS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    message = buy_shop_item(player, idx, payment_mode)
                elif event.key == pygame.K_p:
                    payment_mode = "card" if payment_mode == "cash" else "cash"
                    mode_name = "Cards" if payment_mode == "card" else "Cash"
                    message = f"Payment mode: {mode_name}"

        screen.fill((0, 0, 0))

        title = font.render("General Store", True, (255, 255, 255))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 60))

        money_txt = font.render(f"Money: ${player.money:.0f}", True, (200, 200, 200))
        screen.blit(money_txt, (80, 110))

        duplicates = duplicate_card_rarity_counts(player)
        cards_txt = font.render(
            f"Duplicate Cards: {_format_duplicate_summary(duplicates)}",
            True,
            (200, 200, 200),
        )
        screen.blit(cards_txt, (80, 140))

        for i, item in enumerate(SHOP_ITEMS):
            color = (255, 255, 0) if i == idx else (200, 200, 200)
            price = get_shop_price(player, i)
            card_cost = item.get("card_cost", {})
            req_text = (
                f"Cards: {_format_card_requirements(card_cost)}"
                if card_cost
                else "Cards: N/A"
            )
            text = font.render(
                f"{item['name']} - ${price} | {req_text}",
                True,
                color,
            )
            screen.blit(text, (80, 180 + i * 30))

        mode_name = "Cards" if payment_mode == "card" else "Cash"
        info = font.render(
            f"Mode: {mode_name}  Enter: Buy  P: Toggle payment  Esc: Exit",
            True,
            (200, 200, 200),
        )
        screen.blit(info, (80, settings.SCREEN_HEIGHT - 100))

        if message:
            msg = font.render(message, True, (180, 220, 180))
            screen.blit(msg, (80, settings.SCREEN_HEIGHT - 60))

        pygame.display.flip()
        pygame.time.wait(20)


def business_menu(
    game: "Game", player, screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
) -> None:
    """Menu for managing player owned businesses.

    Displays a list of owned businesses and allows the player to perform
    actions such as managing for bonus profit, hiring staff, running
    marketing campaigns, or training staff.  Arrow keys navigate the list and
    the following hotkeys trigger actions::

        M - Manage
        H - Hire one staff
        C - Run marketing campaign
        T - Train staff
        Esc - Exit

    The menu is intentionally simple since tests call the underlying
    business functions directly; the UI exists mainly for completeness when
    running the game manually.
    """

    screen = screen or game.screen
    font = font or game.font

    if not player.businesses:
        return

    names = list(player.businesses.keys())
    idx = 0
    message = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(names)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(names)
                elif event.key == pygame.K_m:
                    message = manage_business(player, names[idx])
                elif event.key == pygame.K_h:
                    message = hire_staff(player, names[idx])
                elif event.key == pygame.K_c:
                    message = run_marketing_campaign(player, names[idx])
                elif event.key == pygame.K_t:
                    message = train_staff(player, names[idx])
                elif event.key == pygame.K_f:
                    name = names[idx]
                    if name in player.business_futures:
                        message = cash_out_future(player, name)
                    else:
                        message = schedule_future_contract(player, name)

        screen.fill((0, 0, 0))
        title = font.render("Businesses", True, (255, 255, 255))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
        for i, name in enumerate(names):
            staff = player.business_staff.get(name, 0)
            color = (255, 255, 0) if i == idx else (200, 200, 200)
            label = f"{name} (staff {staff})"
            contract = player.business_futures.get(name)
            if contract:
                due = contract.get("day_due", player.day)
                if player.day >= due:
                    label += " [Future ready]"
                else:
                    label += f" [Future day {due}]"
            txt = font.render(label, True, color)
            screen.blit(txt, (100, 120 + i * 40))
        if message:
            msg_txt = font.render(message, True, (200, 200, 200))
            screen.blit(msg_txt, (100, settings.SCREEN_HEIGHT - 80))
        info = font.render(
            "M:Manage H:Hire C:Campaign T:Train F:Futures Esc:Exit",
            True,
            (200, 200, 200),
        )
        screen.blit(info, (100, settings.SCREEN_HEIGHT - 40))
        pygame.display.flip()
        pygame.time.wait(20)


def pause_menu(
    game: "Game", player, screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
):
    """Display the pause menu and handle save/load/options.

    Returns the (potentially replaced) player instance when resuming.
    """
    screen = screen or game.screen
    font = font or game.font
    options = ["Resume", "Save Game", "Load Game", "Options"]
    idx = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return player
                if event.key == pygame.K_UP:
                    idx = (idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = options[idx]
                    if choice == "Resume":
                        return player
                    if choice == "Save Game":
                        save_game(player)
                    elif choice == "Load Game":
                        loaded = load_game()
                        if loaded:
                            player = loaded
                    elif choice == "Options":
                        controls_menu(game, screen, font)

        screen.fill((0, 0, 0))
        title = font.render("Paused", True, (255, 255, 255))
        screen.blit(
            title,
            (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 120),
        )
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == idx else (200, 200, 200)
            txt = font.render(opt, True, color)
            screen.blit(
                txt,
                (settings.SCREEN_WIDTH // 2 - txt.get_width() // 2, 200 + i * 40),
            )
        pygame.display.flip()
        pygame.time.wait(20)


def start_menu(
    game: "Game", screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
) -> bool:
    """Display the start menu. Returns ``True`` if load was chosen."""
    screen = screen or game.screen
    font = font or game.font
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
                if game:
                    game.screen = screen
                recalc_layouts()
                compute_slot_rects()
                font = scaled_font(28)
                if game:
                    game.font = font
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return False
                if event.key == pygame.K_l:
                    return True
                if event.key == pygame.K_c:
                    controls_menu(game, screen, font)
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


def character_creation(
    game: "Game", screen: pygame.Surface | None = None, font: pygame.font.Font | None = None
):
    """Prompt for name and appearance options."""
    screen = screen or game.screen
    font = font or game.font
    name = ""
    colors = [(40, 40, 40), (200, 50, 50), (50, 90, 200)]
    color_names = ["Black", "Red", "Blue"]
    head_colors = [(245, 219, 164), (224, 188, 135), (192, 152, 109)]
    head_color_names = ["Light", "Tan", "Brown"]
    body_idx = 0
    head_idx = 0
    pants_idx = 0
    hat_idx = 0
    has_hat = False
    selecting = 0  # 0=body,1=head,2=pants,3=hat
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return (
                        name or "Player",
                        colors[body_idx],
                        head_colors[head_idx],
                        colors[pants_idx],
                        has_hat,
                        colors[hat_idx],
                    )
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_TAB:
                    selecting = (selecting + 1) % 4
                elif event.key == pygame.K_LEFT:
                    if selecting == 0:
                        body_idx = (body_idx - 1) % len(colors)
                    elif selecting == 1:
                        head_idx = (head_idx - 1) % len(head_colors)
                    elif selecting == 2:
                        pants_idx = (pants_idx - 1) % len(colors)
                    elif selecting == 3 and has_hat:
                        hat_idx = (hat_idx - 1) % len(colors)
                elif event.key == pygame.K_RIGHT:
                    if selecting == 0:
                        body_idx = (body_idx + 1) % len(colors)
                    elif selecting == 1:
                        head_idx = (head_idx + 1) % len(head_colors)
                    elif selecting == 2:
                        pants_idx = (pants_idx + 1) % len(colors)
                    elif selecting == 3 and has_hat:
                        hat_idx = (hat_idx + 1) % len(colors)
                elif event.key == pygame.K_SPACE and selecting == 3:
                    has_hat = not has_hat
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
        pants_txt = font.render(
            f"Pants Color: {color_names[pants_idx]} (\u2190/\u2192)",
            True,
            colors[pants_idx],
        )
        hat_status = "On" if has_hat else "Off"
        hat_color = colors[hat_idx]
        hat_txt = font.render(
            f"Hat: {hat_status} ({color_names[hat_idx]}) (Space)",
            True,
            hat_color if has_hat else (200, 200, 200),
        )
        toggle_txt = font.render("Press TAB to switch", True, (230, 230, 230))
        confirm = font.render("Press Enter to Start", True, (230, 230, 230))
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 220))
        screen.blit(prompt, (settings.SCREEN_WIDTH // 2 - prompt.get_width() // 2, 260))
        screen.blit(
            body_txt, (settings.SCREEN_WIDTH // 2 - body_txt.get_width() // 2, 300)
        )
        screen.blit(
            head_txt, (settings.SCREEN_WIDTH // 2 - head_txt.get_width() // 2, 330)
        )
        screen.blit(
            pants_txt, (settings.SCREEN_WIDTH // 2 - pants_txt.get_width() // 2, 360)
        )
        screen.blit(
            hat_txt, (settings.SCREEN_WIDTH // 2 - hat_txt.get_width() // 2, 390)
        )
        screen.blit(
            toggle_txt, (settings.SCREEN_WIDTH // 2 - toggle_txt.get_width() // 2, 420)
        )
        screen.blit(
            confirm, (settings.SCREEN_WIDTH // 2 - confirm.get_width() // 2, 450)
        )
        pygame.display.flip()
        pygame.time.wait(20)
