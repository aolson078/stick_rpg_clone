"""Quest and event data split from game.py."""

from __future__ import annotations
import os
import json
import random
from typing import List, Tuple

from loaders import load_quests, load_sidequests

import pygame

from entities import Player, Quest, Event, SideQuest, NPC
from inventory import HOME_UPGRADES
from combat import BRAWLER_COUNT

# Epithets awarded for certain achievements
ACHIEVEMENT_EPITHETS = {
    "First Blood": "the Rookie",
    "Brawler Master": "the Brawler",
    "Wealthy": "the Rich",
    "Story Hero": "the Hero",
    "Boss Slayer": "the Slayer",
}

# Names of collectible trading cards
CARD_NAMES = [
    "Slime",
    "Goblin",
    "Knight",
    "Dragon",
    "Merchant",
    "Wizard",
    "Farmer",
    "Pirate",
    "Robot",
    "Alien",
]

# Storyline quests completed in order
QUESTS: List[Quest] = load_quests()

# Building targets for quest markers
QUEST_TARGETS = {
    0: "job",
    1: "gym",
    2: "library",
    3: "job",
    4: "gym",
    5: "dungeon",
    6: "home",
}

# Optional side quests
SIDE_QUESTS = load_sidequests()
SIDE_QUEST = SIDE_QUESTS.get("Bank Delivery")
NPC_QUEST = SIDE_QUESTS.get("Courier Errand")
MALL_QUEST = SIDE_QUESTS.get("Beach Delivery")

# Friendly townsfolk found around the city
NPCS = [
    NPC(pygame.Rect(500, 500, 40, 40), "Sam", NPC_QUEST),
    NPC(pygame.Rect(600, 400, 40, 40), "Alice", None, True, "F"),
    NPC(pygame.Rect(700, 600, 40, 40), "Bella", None, True, "F"),
    NPC(pygame.Rect(400, 700, 40, 40), "Chris", None, True, "M"),
]

# Main storyline quests progressed via story_stage
STORY_QUESTS = [
    Quest("Visit the Town Hall", lambda p: p.story_stage >= 1),
    Quest("Choose an allegiance", lambda p: p.story_stage >= 2),
    Quest("Prove your loyalty", lambda p: p.story_stage >= 3),
    Quest("Report back to your ally", lambda p: p.story_stage >= 4),
]

# Suggested locations for story objectives
STORY_TARGETS = {
    0: "townhall",
    1: "townhall",
    2: "dungeon",
    3: "townhall",
}


# Event helpers


def _ev_found_money(p: Player) -> None:
    """Give the player a small amount of money."""
    p.money += 5
    bonus = 5 * p.perk_levels.get("Lucky", 0)
    p.money += 5 + bonus


def _ev_gain_int(p: Player) -> None:
    """Increase player's intelligence by one."""
    p.intelligence += 1
    p.intelligence += 1 + p.perk_levels.get("Lucky", 0)


def _ev_gain_cha(p: Player) -> None:
    """Increase player's charisma by one."""
    p.charisma += 1
    p.charisma += 1 + p.perk_levels.get("Lucky", 0)


def _ev_trip(p: Player) -> None:
    """Reduce player health to simulate tripping."""
    p.health = max(p.health - 5, 0)


def _ev_theft(p: Player) -> None:
    """Steal some money from the player."""
    p.money = max(p.money - 10, 0)


def _ev_free_food(p: Player) -> None:
    """Give player energy restoring food."""
    p.energy = min(100, p.energy + 10 + 2 * p.perk_levels.get("Lucky", 0))


def _ev_help_reward(p: Player) -> None:
    """Reward player for helping someone."""
    p.money += 15 + 5 * p.perk_levels.get("Lucky", 0)


def _ev_found_token(p: Player) -> None:
    """Give the player a casino token."""
    p.tokens += 1


def _ev_found_metal(p: Player) -> None:
    """Add scrap metal to the player's resources."""
    p.resources["metal"] = p.resources.get("metal", 0) + 1


def _ev_found_cloth(p: Player) -> None:
    """Add a piece of cloth to the player's resources."""
    p.resources["cloth"] = p.resources.get("cloth", 0) + 1


def _ev_found_herb(p: Player) -> None:
    """Add an herb to the player's resources."""
    p.resources["herbs"] = p.resources.get("herbs", 0) + 1


def _ev_found_card(p: Player) -> None:
    """Grant a random trading card that hasn't been collected yet."""
    remaining = [c for c in CARD_NAMES if c not in p.cards]
    if remaining:
        p.cards.append(random.choice(remaining))


EVENTS = [
    Event("You found $5 on the ground!", _ev_found_money),
    Event("Someone shared a study tip. +1 INT", _ev_gain_int),
    Event("You chatted with locals. +1 CHA", _ev_gain_cha),
    Event("You tripped and hurt yourself. -5 health", _ev_trip),
    Event("A thief stole $10 from you!", _ev_theft),
    Event("A stranger gave you a meal. +10 energy", _ev_free_food),
    Event("You helped someone and got $15", _ev_help_reward),
    Event("Found a casino token!", _ev_found_token),
    Event("Picked up some scrap metal", _ev_found_metal),
    Event("Found a piece of cloth", _ev_found_cloth),
    Event("Gathered herbs nearby", _ev_found_herb),
    Event("You found a trading card!", _ev_found_card),
]

SEASON_EVENTS = {
    "Spring": [
        Event(
            "Flowers bloom brightly. +1 CHA",
            lambda p: setattr(p, "charisma", p.charisma + 1),
        ),
    ],
    "Summer": [
        Event(
            "Heat wave tires you out. -5 energy",
            lambda p: setattr(p, "energy", max(p.energy - 5, 0)),
        ),
    ],
    "Fall": [
        Event(
            "Found $5 under fallen leaves",
            lambda p: setattr(p, "money", p.money + 5),
        ),
    ],
    "Winter": [
        Event(
            "Cold wind toughens you. +1 DEF",
            lambda p: setattr(p, "defense", p.defense + 1),
        ),
    ],
}

WEATHER_EVENTS = {
    "Rain": [
        Event(
            "Got soaked in the rain. -5 energy",
            lambda p: setattr(p, "energy", max(p.energy - 5, 0)),
        ),
    ],
    "Snow": [
        Event(
            "Built a snowman for fun. +1 CHA",
            lambda p: setattr(p, "charisma", p.charisma + 1),
        ),
    ],
}

LOCATION_EVENTS = {
    "beach": [
        Event(
            "You found a seashell worth $5",
            lambda p: setattr(p, "money", p.money + 5),
        ),
    ],
    "mall": [
        Event(
            "A flash sale cost you $5",
            lambda p: setattr(p, "money", max(p.money - 5, 0)),
        ),
    ],
}

# Time-specific events that occur only during certain hours
TIMED_EVENTS: List[Tuple[int, int, Event]] = [
    (
        6,
        9,
        Event(
            "You went jogging with a stranger. +1 STR",
            lambda p: setattr(p, "strength", p.strength + 1),
        ),
    ),
    (
        18,
        22,
        Event(
            "Street performer inspired you. +1 CHA",
            lambda p: setattr(p, "charisma", p.charisma + 1),
        ),
    ),
    (
        20,
        24,
        Event(
            "Late-night snack stand boosted your energy",
            lambda p: setattr(p, "energy", min(100, p.energy + 10)),
        ),
    ),
]

EVENT_CHANCE = 0.0004


def random_event(player: Player, location: str | None = None) -> str | None:
    """Possibly trigger a random event and return its description."""
    if random.random() < EVENT_CHANCE:
        hour = int(player.time) // 60
        pool = EVENTS.copy()
        pool.extend(SEASON_EVENTS.get(player.season, []))
        pool.extend(WEATHER_EVENTS.get(player.weather, []))
        if location and location in LOCATION_EVENTS:
            pool.extend(LOCATION_EVENTS[location])
        for start, end, tev in TIMED_EVENTS:
            if start <= end:
                if start <= hour < end:
                    pool.append(tev)
            else:
                if hour >= start or hour < end:
                    pool.append(tev)
        ev = random.choice(pool)
        ev.apply(player)
        return ev.description
    return None


def update_npcs():
    """Move NPCs randomly around the city map."""
    for npc in NPCS:
        if random.random() < 0.05:
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            rect = npc.rect.move(dx * 4, dy * 4)
            if 0 <= rect.x <= 1600 - 40 and 0 <= rect.y <= 1200 - 40:
                npc.rect = rect


def advance_story(player: Player) -> None:
    """Advance the story if branch objectives are completed."""
    if player.story_branch == "mayor" and player.story_stage == 2:
        if player.enemies_defeated >= 3:
            player.story_stage = 3
    if player.story_branch == "gang" and player.story_stage == 2:
        if player.gang_package_done:
            player.story_stage = 3


def check_story(player: Player) -> bool:
    """Mark story quests completed based on current story stage."""
    changed = False
    for i, q in enumerate(STORY_QUESTS):
        if not q.completed and q.check(player):
            q.completed = True
            changed = True
    return changed


LEADERBOARD_FILE = "leaderboard.json"


def update_leaderboard(player: Player) -> None:
    """Save the player's completion stats to a leaderboard file."""
    record = {"day": player.day, "money": int(player.money)}
    board: List[dict] = []
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            try:
                board = json.load(f)
            except Exception:
                board = []
    board.append(record)
    board = sorted(board, key=lambda r: (r["day"], -r["money"]))[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f)


def check_quests(player: Player) -> bool:
    """Advance the main quest line if the current objective is met."""
    new = False
    if player.current_quest < len(QUESTS):
        q = QUESTS[player.current_quest]
        if not q.completed and q.check(player):
            q.completed = True
            new = True
            if q.reward:
                q.reward(player)
            if q.next_index is not None:
                player.current_quest = q.next_index
            else:
                player.current_quest = len(QUESTS)
    return new


def check_perk_unlocks(player: Player) -> bool:
    """Grant perk points when stat thresholds are reached."""
    gained = False
    if player.strength >= player.next_strength_perk:
        player.perk_points += 1
        player.next_strength_perk += 5
        gained = True
    if player.intelligence >= player.next_intelligence_perk:
        player.perk_points += 1
        player.next_intelligence_perk += 5
        gained = True
    if player.charisma >= player.next_charisma_perk:
        player.perk_points += 1
        player.next_charisma_perk += 5
        gained = True
    return gained


def check_hidden_perks(player: Player) -> str | None:
    """Unlock secret perks when requirements are met."""
    if player.brawls_won >= BRAWLER_COUNT and "Bar Champion" not in player.perk_levels:
        player.perk_levels["Bar Champion"] = 1
        return "Secret perk unlocked: Bar Champion!"
    if (
        set(player.home_upgrades) == {u[0] for u in HOME_UPGRADES}
        and "Home Owner" not in player.perk_levels
    ):
        player.perk_levels["Home Owner"] = 1
        return "Secret perk unlocked: Home Owner!"
    if player.boss_defeated and "Champion" not in player.perk_levels:
        player.perk_levels["Champion"] = 1
        return "Secret perk unlocked: Champion!"
    return None


def check_achievements(player: Player) -> str | None:
    """Unlock achievements based on notable milestones."""
    if "First Blood" not in player.achievements and player.enemies_defeated >= 1:
        player.achievements.append("First Blood")
        player.epithet = ACHIEVEMENT_EPITHETS.get("First Blood", player.epithet)
        return "Achievement unlocked: First Blood!"
    if (
        "Brawler Master" not in player.achievements
        and player.brawls_won >= BRAWLER_COUNT
    ):
        player.achievements.append("Brawler Master")
        player.epithet = ACHIEVEMENT_EPITHETS.get("Brawler Master", player.epithet)
        return "Achievement unlocked: Brawler Master!"
    if "Wealthy" not in player.achievements and player.money >= 1000:
        player.achievements.append("Wealthy")
        player.epithet = ACHIEVEMENT_EPITHETS.get("Wealthy", player.epithet)
        return "Achievement unlocked: Wealthy!"
    if "Story Hero" not in player.achievements and all(
        q.completed for q in STORY_QUESTS
    ):
        player.achievements.append("Story Hero")
        update_leaderboard(player)
        player.epithet = ACHIEVEMENT_EPITHETS.get("Story Hero", player.epithet)
        return "Achievement unlocked: Story Hero!"
    if "Boss Slayer" not in player.achievements and player.boss_defeated:
        player.achievements.append("Boss Slayer")
        player.epithet = ACHIEVEMENT_EPITHETS.get("Boss Slayer", player.epithet)
        return "Achievement unlocked: Boss Slayer!"
    return None
