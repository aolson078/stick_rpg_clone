"""Utility functions split from game.py for easier maintenance."""

from __future__ import annotations

import json
import os
import random
import time
from typing import Dict, List, Optional

import pygame

from entities import Player, Building, InventoryItem
from quests import (
    QUESTS,
    SIDE_QUESTS,
    STORY_QUESTS,
    SIDE_QUEST,
    NPC_QUEST,
    STORY_TARGETS,
    QUEST_TARGETS,
    SEASONAL_QUESTS,
)
from combat import energy_cost
from businesses import collect_profits
import settings


BASE_SCREEN_W, BASE_SCREEN_H = 1600, 1200


# --- Layout helpers -------------------------------------------------------

HOME_WIDTH = settings.SCREEN_WIDTH
HOME_HEIGHT = settings.SCREEN_HEIGHT
BED_RECT = pygame.Rect(0, 0, 0, 0)
DOOR_RECT = pygame.Rect(0, 0, 0, 0)
FURNITURE_RECTS: List[pygame.Rect] = []

# Bonuses granted when sleeping with certain furniture placed
FURNITURE_BONUSES: Dict[str, Dict[str, int]] = {
    "Decor Chair": {"charisma": 1},
}

BAR_WIDTH = settings.SCREEN_WIDTH
BAR_HEIGHT = settings.SCREEN_HEIGHT
BAR_DOOR_RECT = pygame.Rect(0, 0, 0, 0)
COUNTER_RECT = pygame.Rect(0, 0, 0, 0)
BJ_RECT = pygame.Rect(0, 0, 0, 0)
SLOT_RECT = pygame.Rect(0, 0, 0, 0)
BRAWL_RECT = pygame.Rect(0, 0, 0, 0)
DART_RECT = pygame.Rect(0, 0, 0, 0)

FOREST_WIDTH = settings.SCREEN_WIDTH
FOREST_HEIGHT = settings.SCREEN_HEIGHT
FOREST_DOOR_RECT = pygame.Rect(0, 0, 0, 0)


def scaled_font(base_size: int) -> pygame.font.Font:
    """Return a font scaled relative to the window height."""
    scale = settings.SCREEN_HEIGHT / BASE_SCREEN_H
    return pygame.font.SysFont(None, int(base_size * scale))


def recalc_layouts() -> None:
    """Update layout rects when the window size changes."""
    global HOME_WIDTH, HOME_HEIGHT, BED_RECT, DOOR_RECT
    global BAR_WIDTH, BAR_HEIGHT, BAR_DOOR_RECT, COUNTER_RECT
    global BJ_RECT, SLOT_RECT, BRAWL_RECT, DART_RECT
    global FOREST_WIDTH, FOREST_HEIGHT, FOREST_DOOR_RECT
    global FURNITURE_RECTS

    HOME_WIDTH = settings.SCREEN_WIDTH
    HOME_HEIGHT = settings.SCREEN_HEIGHT

    # Home layout ratios based on the original 1600x1200 resolution
    bed = (
        int(HOME_WIDTH * 0.075),
        int(HOME_HEIGHT * 0.1333),
        int(HOME_WIDTH * 0.1375),
        int(HOME_HEIGHT * 0.1),
    )
    BED_RECT = pygame.Rect(*bed)
    door_w = int(HOME_WIDTH * 0.075)
    door_h = int(HOME_HEIGHT * 0.1333)
    DOOR_RECT = pygame.Rect(
        int(HOME_WIDTH * 0.5 - HOME_WIDTH * 0.0375),
        int(HOME_HEIGHT * 0.85),
        door_w,
        door_h,
    )

    col_spacing = int(HOME_WIDTH * 0.09375)
    row_spacing = int(HOME_HEIGHT * 0.0833)
    base_x = int(HOME_WIDTH * 0.225)
    base_y = int(HOME_HEIGHT * 0.4333)
    furn_w = int(HOME_WIDTH * 0.075)
    furn_h = int(HOME_HEIGHT * 0.0667)
    FURNITURE_RECTS = [
        pygame.Rect(base_x + col * col_spacing, base_y + row * row_spacing, furn_w, furn_h)
        for row in range(3)
        for col in range(3)
    ]

    BAR_WIDTH = settings.SCREEN_WIDTH
    BAR_HEIGHT = settings.SCREEN_HEIGHT
    BAR_DOOR_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.5 - BAR_WIDTH * 0.0375),
        int(BAR_HEIGHT * 0.85),
        door_w,
        door_h,
    )
    COUNTER_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.0375),
        int(BAR_HEIGHT * 0.45),
        int(BAR_WIDTH * 0.1125),
        int(BAR_HEIGHT * 0.1),
    )
    BJ_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.4375),
        int(BAR_HEIGHT * 0.375),
        int(BAR_WIDTH * 0.125),
        int(BAR_HEIGHT * 0.0833),
    )
    SLOT_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.85),
        int(BAR_HEIGHT * 0.45),
        int(BAR_WIDTH * 0.1125),
        int(BAR_HEIGHT * 0.1),
    )
    BRAWL_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.45),
        int(BAR_HEIGHT * 0.0667),
        int(BAR_WIDTH * 0.1),
        int(BAR_HEIGHT * 0.1),
    )
    DART_RECT = pygame.Rect(
        int(BAR_WIDTH * 0.4375),
        int(BAR_HEIGHT * 0.55),
        int(BAR_WIDTH * 0.125),
        int(BAR_HEIGHT * 0.0833),
    )

    FOREST_WIDTH = settings.SCREEN_WIDTH
    FOREST_HEIGHT = settings.SCREEN_HEIGHT
    FOREST_DOOR_RECT = pygame.Rect(
        int(FOREST_WIDTH * 0.5 - FOREST_WIDTH * 0.0375),
        int(FOREST_HEIGHT * 0.85),
        door_w,
        door_h,
    )


# Initialize rects using current screen size
recalc_layouts()

# --- Inventory UI helpers -------------------------------------------------


def compute_slot_rects() -> Dict[str, pygame.Rect]:
    """Return rects for each equipment slot."""
    left = settings.SCREEN_WIDTH // 10
    top = settings.SCREEN_HEIGHT // 6
    w = int(settings.SCREEN_WIDTH * 0.0625)
    h = int(settings.SCREEN_HEIGHT * 0.05)
    spacing = int(settings.SCREEN_HEIGHT * 0.0583)
    return {
        "head": pygame.Rect(left, top, w, h),
        "chest": pygame.Rect(left, top + spacing, w, h),
        "arms": pygame.Rect(left, top + spacing * 2, w, h),
        "legs": pygame.Rect(left, top + spacing * 3, w, h),
        "weapon": pygame.Rect(left, top + spacing * 4, w, h),
    }


def compute_hotkey_rects() -> List[pygame.Rect]:
    """Return rects for quick item hotkey slots."""
    w = int(settings.SCREEN_WIDTH * 0.0375)
    h = int(settings.SCREEN_HEIGHT * 0.0333)
    spacing = int(settings.SCREEN_WIDTH * 0.04375)
    total_width = w + spacing * 4
    base = settings.SCREEN_WIDTH // 2 - total_width // 2
    y = settings.SCREEN_HEIGHT - int(settings.SCREEN_HEIGHT * 0.0667)
    return [pygame.Rect(base + i * spacing, y, w, h) for i in range(5)]


def compute_furniture_rects(player: Player) -> List[pygame.Rect]:
    """Return rects for movable home furniture."""
    rects = []
    for i, base in enumerate(FURNITURE_RECTS, 1):
        pos = player.furniture_pos.get(f"slot{i}", (base.x, base.y))
        rects.append(pygame.Rect(pos[0], pos[1], base.width, base.height))
    return rects


def init_furniture_positions(player: Player) -> None:
    """Initialize furniture slots if coordinates are unset."""
    for i, base in enumerate(FURNITURE_RECTS, 1):
        slot = f"slot{i}"
        if player.furniture_pos.get(slot) == (0, 0):
            player.furniture_pos[slot] = (base.x, base.y)


# --- Quest helpers -------------------------------------------------------


def quest_target_building(
    player: Player, buildings: List[Building]
) -> Optional[Building]:
    """Return the building associated with the player's current objective."""
    if player.side_quest:
        sq = SIDE_QUESTS.get(player.side_quest)
        if sq:
            return next((b for b in buildings if b.btype == sq.target), None)
    if player.story_stage < len(STORY_QUESTS):
        target = STORY_TARGETS.get(player.story_stage)
        if target:
            if target == "dungeon" and player.story_branch == "gang":
                target = "dealer"
            return next((b for b in buildings if b.btype == target), None)
    if player.current_quest < len(QUESTS):
        t = QUEST_TARGETS.get(player.current_quest)
        if t:
            return next((b for b in buildings if b.btype == t), None)
    return None


# --- Building and weather helpers ---------------------------------------

OPEN_HOURS = {
    "home": (0, 24),
    "job": (8, 18),
    "shop": (9, 21),
    "gym": (6, 22),
    "library": (8, 20),
    "park": (6, 22),
    "dealer": (20, 4),
    "clinic": (8, 18),
    "bar": (18, 2),
    "dungeon": (0, 24),
    "petshop": (9, 19),
    "bank": (9, 17),
    "townhall": (9, 17),
    "workshop": (8, 20),
    "farm": (6, 20),
    "forest": (0, 24),
    "business": (8, 18),
    "mall": (10, 21),
    "suburbs": (0, 24),
    "beach": (6, 20),
    "boss": (0, 24),
}

SEASONS = ["Spring", "Summer", "Fall", "Winter"]
WEATHERS = ["Clear", "Rain", "Snow"]
def building_open(btype: str, minutes: float, player: Player) -> bool:
    """Check if a building type is open at the given time."""
    start, end = OPEN_HOURS.get(btype, (0, 24))
    hour = (minutes / 60) % 24
    if start <= end:
        open_now = start <= hour < end
    else:
        open_now = hour >= start or hour < end
    if not open_now:
        return False
    if btype in ("park", "dealer") and player.weather in ("Rain", "Snow"):
        return False
    if btype == "park" and player.season == "Winter":
        return False
    if btype == "boss" and player.current_quest < len(QUESTS):
        return False
    return True


def update_weather(player: Player) -> None:
    """Randomly set the current season and weather.

    When a new season begins, award the matching seasonal quest if the
    player doesn't already have a side quest.
    """
    old_season = player.season
    season_index = ((player.day - 1) // 30) % len(SEASONS)
    player.season = SEASONS[season_index]
    if player.season != old_season and player.side_quest is None:
        quest = SEASONAL_QUESTS.get(player.season)
        if quest:
            player.side_quest = quest.name
    if player.season == "Winter":
        choices = ["Snow", "Snow", "Clear", "Rain"]
    elif player.season == "Summer":
        choices = ["Clear", "Clear", "Rain"]
    elif player.season == "Spring":
        choices = ["Rain", "Clear", "Clear"]
    else:  # Fall
        choices = ["Clear", "Rain", "Snow"]
    player.weather = random.choice(choices)


def advance_day(player: Player) -> int:
    """Increment the day counter and apply daily effects."""
    player.day += 1
    update_weather(player)
    interest = int(player.bank_balance * 0.01)
    player.bank_balance += interest
    save_game(player)
    return interest


def sleep(player: Player) -> Optional[str]:
    """Restore energy, advance the day, and handle home bonuses."""
    player.energy = 100
    if "Comfy Bed" in player.home_upgrades:
        player.energy += 20
    player.energy += 10 * player.perk_levels.get("Night Owl", 0)
    player.time = 8 * 60
    interest = advance_day(player)
    if "Decorations" in player.home_upgrades:
        player.charisma += 1
    if "Study Desk" in player.home_upgrades:
        player.intelligence += 1
    if "Home Gym" in player.home_upgrades:
        player.strength += 1
    if "Private Library" in player.home_upgrades:
        player.intelligence += 2
    if player.perk_levels.get("Home Owner"):
        player.health = min(player.health + 10, 100)

    for item in player.furniture.values():
        if item and item.name in FURNITURE_BONUSES:
            for stat, val in FURNITURE_BONUSES[item.name].items():
                setattr(player, stat, getattr(player, stat) + val)
    messages: List[str] = []
    if player.companion == "Dog":
        chance = 0.2 + 0.2 * (player.companion_level - 1)
        amount = 5 * player.companion_level
        if random.random() < chance:
            player.money += amount
            messages.append(f"Your dog brought you ${amount}!")
    if "Garden" in player.home_upgrades and random.random() < 0.3:
        player.money += 10
        messages.append("Found $10 in the garden")
    if "Arcade Room" in player.home_upgrades and random.random() < 0.3:
        player.tokens += 1
        messages.append("Won a token in your arcade")
    profits = collect_profits(player)
    if profits:
        messages.append(f"Your businesses earned ${profits}")
    if interest:
        messages.append(f"Earned ${interest} interest")
    return " ".join(messages) if messages else None


# --- Mini activities -----------------------------------------------------


def play_blackjack(player: Player, difficulty: str = "normal") -> str:
    """Play a simple blackjack game using one token.

    Difficulty adjusts dealer skill and rewards. Achieving a perfect
    score on hard mode grants a unique card and achievement.
    """
    if player.tokens < 1:
        return "No tokens left!"

    if difficulty not in {"easy", "normal", "hard"}:
        raise ValueError("Invalid difficulty")

    player.tokens -= 1
    player_score = random.randint(16, 23)

    # Dealer skill varies with difficulty
    dealer_low = 15 if difficulty == "easy" else 16
    if difficulty == "hard":
        dealer_low = 18
    dealer_score = random.randint(dealer_low, 23)

    win_reward = 2
    if difficulty == "hard":
        win_reward = 3

    if player_score > 21:
        return "Bust!"
    if dealer_score > 21 or player_score > dealer_score:
        player.tokens += win_reward
        # Perfect score on hard unlocks rewards
        if (
            difficulty == "hard"
            and player_score == 21
            and "Blackjack Champion" not in player.achievements
        ):
            player.achievements.append("Blackjack Champion")
            if "Blackjack Shark" not in player.cards:
                player.cards.append("Blackjack Shark")
        return f"You win! +{win_reward} tokens"
    if player_score == dealer_score:
        player.tokens += 1
        return "Push. Token returned"
    return "Dealer wins"


def play_slots(player: Player) -> str:
    """Spin the slot machine to try for token rewards."""
    if player.tokens < 1:
        return "No tokens left!"
    player.tokens -= 1
    roll = random.random()
    if roll < 0.05:
        player.tokens += 5
        return "Jackpot! +5 tokens"
    if roll < 0.2:
        player.tokens += 2
        return "You won 2 tokens"
    return "No win"


def play_darts(player: Player, difficulty: str = "normal") -> str:
    """Throw darts to win tokens based on your score.

    Higher difficulties reduce your score but award more tokens.
    Landing a bullseye on hard grants a collectible card and achievement.
    """
    if player.tokens < 1:
        return "No tokens left!"
    if difficulty not in {"easy", "normal", "hard"}:
        raise ValueError("Invalid difficulty")
    player.tokens -= 1
    score = random.randint(1, 20) + player.speed // 2
    if difficulty == "easy":
        score += 2
    elif difficulty == "hard":
        score -= 2

    if score >= 20:
        reward = 2
        if difficulty == "hard":
            reward = 3
            if "Darts Champion" not in player.achievements:
                player.achievements.append("Darts Champion")
                if "Dart Master" not in player.cards:
                    player.cards.append("Dart Master")
        player.tokens += reward
        return f"Bullseye! +{reward} tokens"
    if score >= 15:
        reward = 1
        if difficulty == "hard":
            reward = 2
        player.tokens += reward
        return f"Nice shot! +{reward} token" + ("s" if reward > 1 else "")
    return "Missed the board"


def go_fishing(player: Player, difficulty: str = "normal") -> str:
    """Fish at the park and possibly earn money or herbs.

    Hard difficulty yields higher potential rewards but more failures.
    Reeling in a big catch on hard unlocks a special card and achievement.
    """
    if player.energy < 5:
        return "Too tired to fish!"
    if difficulty not in {"easy", "normal", "hard"}:
        raise ValueError("Invalid difficulty")
    player.energy -= energy_cost(player, 5)

    no_bite_chance = 0.3
    herb_chance = 0.2
    min_reward, max_reward = 5, 20
    if difficulty == "easy":
        no_bite_chance = 0.2
    elif difficulty == "hard":
        no_bite_chance = 0.5
        min_reward, max_reward = 10, 30

    if random.random() < no_bite_chance:
        return "Nothing was biting"
    if random.random() < herb_chance:
        player.resources["herbs"] = player.resources.get("herbs", 0) + 1
        return "Found some herbs by the water"

    reward = random.randint(min_reward, max_reward)
    player.money += reward
    if (
        difficulty == "hard"
        and reward >= 25
        and "Master Angler" not in player.achievements
    ):
        player.achievements.append("Master Angler")
        if "Fishing Legend" not in player.cards:
            player.cards.append("Fishing Legend")
    return f"Caught a fish! +${reward}"


def solve_puzzle(player: Player) -> str:
    """Attempt the library puzzle for a cash reward."""
    if player.energy < 5:
        return "Too tired to think!"
    player.energy -= energy_cost(player, 5)
    chance = player.intelligence + random.randint(0, 10)
    if chance > 12:
        reward = random.randint(10, 20)
        player.money += reward
        return f"Puzzle solved! +${reward}"
    return "Couldn't solve it"


def dig_for_treasure(player: Player) -> str:
    """Dig on the beach for cash or rare items."""
    if player.energy < 5:
        return "Too tired to dig!"
    player.energy -= energy_cost(player, 5)
    roll = random.random()
    if roll < 0.5:
        return "Found nothing."
    if roll < 0.8:
        amount = random.randint(5, 15)
        player.money += amount
        return f"Found ${amount} buried in the sand"
    if roll < 0.95:
        player.inventory.append(InventoryItem("Golden Seashell", "furniture"))
        return "You unearthed a Golden Seashell!"
    player.inventory.append(
        InventoryItem("Pearl Necklace", "chest", defense=1, speed=1)
    )

    return "You dug up a Pearl Necklace!"


# --- Persistence ---------------------------------------------------------
SAVE_FILE = "savegame.json"


def save_game(player: Player) -> None:
    """Serialize all player data to disk."""
    data = {
        "name": player.name,
        "color": list(player.color),
        "head_color": list(player.head_color),
        "money": player.money,
        "energy": player.energy,
        "health": player.health,
        "day": player.day,
        "time": player.time,
        "strength": player.strength,
        "intelligence": player.intelligence,
        "charisma": player.charisma,
        "defense": player.defense,
        "speed": player.speed,
        "office_level": player.office_level,
        "office_shifts": player.office_shifts,
        "dealer_level": player.dealer_level,
        "dealer_shifts": player.dealer_shifts,
        "clinic_level": player.clinic_level,
        "clinic_shifts": player.clinic_shifts,
        "office_exp": player.office_exp,
        "dealer_exp": player.dealer_exp,
        "clinic_exp": player.clinic_exp,
        "tokens": player.tokens,
        "crafting_level": player.crafting_level,
        "crafting_exp": player.crafting_exp,
        "brawls_won": player.brawls_won,
        "enemies_defeated": player.enemies_defeated,
        "boss_defeated": player.boss_defeated,
        "companion": player.companion,
        "companion_level": player.companion_level,
        "companion_abilities": player.companion_abilities,
        "has_skateboard": player.has_skateboard,
        "home_upgrades": player.home_upgrades,
        "home_level": player.home_level,
        "bank_balance": player.bank_balance,
        "perk_points": player.perk_points,
        "perk_levels": player.perk_levels,
        "next_strength_perk": player.next_strength_perk,
        "next_intelligence_perk": player.next_intelligence_perk,
        "next_charisma_perk": player.next_charisma_perk,
        "businesses": player.businesses,
        "business_bonus": player.business_bonus,
        "current_quest": player.current_quest,
        "inventory": [item.__dict__ for item in player.inventory],
        "equipment": {
            slot: (it.__dict__ if it else None) for slot, it in player.equipment.items()
        },
        "hotkeys": [it.__dict__ if it else None for it in player.hotkeys],
        "furniture": {
            slot: (it.__dict__ if it else None) for slot, it in player.furniture.items()
        },
        "furniture_pos": player.furniture_pos,
        "furniture_rot": player.furniture_rot,
        "relationships": player.relationships,
        "last_talk": player.last_talk,
        "romanced": player.romanced,
        "relationship_stage": player.relationship_stage,
        "married_to": player.married_to,
        "reputation": player.reputation,
        "x": player.rect.x,
        "y": player.rect.y,
        "quests": [q.completed for q in QUESTS],
        "npc_progress": player.npc_progress,
        "story_stage": player.story_stage,
        "story_branch": player.story_branch,
        "gang_package_done": player.gang_package_done,
        "resources": player.resources,
        "crops": player.crops,
        "season": player.season,
        "weather": player.weather,
        "achievements": player.achievements,
        "cards": player.cards,
        "known_recipes": player.known_recipes,
        "epithet": player.epithet,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


_last_auto_save = 0.0


def auto_save(player: Player, cooldown: float = 60.0) -> bool:
    """Automatically save the game if the cooldown has elapsed.

    Parameters
    ----------
    player:
        The current player instance whose state should be saved.
    cooldown:
        Minimum number of real-time seconds between automatic saves.

    Returns
    -------
    bool
        ``True`` if the game was saved, ``False`` otherwise.
    """

    global _last_auto_save
    now = time.time()
    if now - _last_auto_save >= cooldown:
        save_game(player)
        _last_auto_save = now
        return True
    return False


def load_game() -> Optional[Player]:
    """Load saved player state if a save file exists."""
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE) as f:
        data = json.load(f)
    player = Player(
        pygame.Rect(
            data.get("x", settings.MAP_WIDTH // 2),
            data.get("y", settings.MAP_HEIGHT // 2),
            settings.PLAYER_SIZE,
            settings.PLAYER_SIZE,
        )
    )
    player.name = data.get("name", player.name)
    player.color = tuple(data.get("color", list(player.color)))
    player.head_color = tuple(data.get("head_color", list(player.head_color)))
    player.money = data.get("money", player.money)
    player.energy = data.get("energy", player.energy)
    player.health = data.get("health", player.health)
    player.day = data.get("day", player.day)
    player.time = data.get("time", player.time)
    player.strength = data.get("strength", player.strength)
    player.intelligence = data.get("intelligence", player.intelligence)
    player.charisma = data.get("charisma", player.charisma)
    player.defense = data.get("defense", player.defense)
    player.speed = data.get("speed", player.speed)
    player.office_level = data.get("office_level", player.office_level)
    player.office_shifts = data.get("office_shifts", player.office_shifts)
    player.office_exp = data.get("office_exp", 0)
    player.dealer_level = data.get("dealer_level", player.dealer_level)
    player.dealer_shifts = data.get("dealer_shifts", player.dealer_shifts)
    player.dealer_exp = data.get("dealer_exp", 0)
    player.clinic_level = data.get("clinic_level", player.clinic_level)
    player.clinic_shifts = data.get("clinic_shifts", player.clinic_shifts)
    player.clinic_exp = data.get("clinic_exp", 0)
    player.tokens = data.get("tokens", player.tokens)
    player.crafting_level = data.get("crafting_level", 1)
    player.crafting_exp = data.get("crafting_exp", 0)
    player.brawls_won = data.get("brawls_won", 0)
    player.enemies_defeated = data.get("enemies_defeated", 0)
    player.boss_defeated = data.get("boss_defeated", False)
    player.has_skateboard = data.get("has_skateboard", player.has_skateboard)
    player.home_upgrades = data.get("home_upgrades", [])
    player.home_level = data.get("home_level", 1)
    player.businesses = data.get("businesses", {})
    player.business_bonus = data.get("business_bonus", {})
    player.bank_balance = data.get("bank_balance", 0.0)
    player.perk_points = data.get("perk_points", 0)
    player.perk_levels = data.get("perk_levels", {})
    player.next_strength_perk = data.get("next_strength_perk", 5)
    player.next_intelligence_perk = data.get("next_intelligence_perk", 5)
    player.next_charisma_perk = data.get("next_charisma_perk", 5)
    player.current_quest = data.get("current_quest", 0)
    player.enemies_defeated = data.get("enemies_defeated", 0)
    player.companion = data.get("companion")
    player.companion_level = data.get("companion_level", 0)
    player.companion_abilities = data.get("companion_abilities", {})
    player.npc_progress = data.get("npc_progress", {})
    player.story_stage = data.get("story_stage", 0)
    player.story_branch = data.get("story_branch")
    player.gang_package_done = data.get("gang_package_done", False)
    player.resources = data.get(
        "resources", {"metal": 0, "cloth": 0, "herbs": 0, "seeds": 0, "produce": 0}
    )
    player.crops = data.get("crops", [])
    player.season = data.get("season", "Spring")
    player.weather = data.get("weather", "Clear")
    player.achievements = data.get("achievements", [])
    player.cards = data.get("cards", [])
    player.known_recipes = data.get("known_recipes", [])
    player.epithet = data.get("epithet", "")
    for item in data.get("inventory", []):
        player.inventory.append(InventoryItem(**item))
    for slot, item in data.get("equipment", {}).items():
        if item:
            player.equipment[slot] = InventoryItem(**item)
    player.hotkeys = [
        InventoryItem(**it) if it else None for it in data.get("hotkeys", [None] * 5)
    ]
    player.furniture = {
        slot: (InventoryItem(**it) if it else None)
        for slot, it in data.get(
            "furniture", {f"slot{i}": None for i in range(1, 10)}
        ).items()
    }
    player.furniture_pos = {
        slot: tuple(pos)
        for slot, pos in data.get(
            "furniture_pos", {f"slot{i}": (0, 0) for i in range(1, 10)}
        ).items()
    }
    player.furniture_rot = {
        slot: int(rot)
        for slot, rot in data.get(
            "furniture_rot", {f"slot{i}": 0 for i in range(1, 10)}
        ).items()
    }
    player.relationships = data.get("relationships", {})
    player.last_talk = data.get("last_talk", {})
    player.romanced = data.get("romanced", [])
    player.relationship_stage = data.get("relationship_stage", {})
    player.married_to = data.get("married_to")
    player.reputation = data.get(
        "reputation", {"mayor": 0, "business": 0, "gang": 0}
    )
    for completed, q in zip(data.get("quests", []), QUESTS):
        q.completed = completed
    return player
