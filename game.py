import sys
import os
import json
import random
import pygame

from entities import Player, Building, Quest, Event, InventoryItem, SideQuest, NPC
from rendering import (
    draw_player,
    draw_player_sprite,
    load_player_sprites,
    draw_building,
    draw_road_and_sidewalks,
    draw_city_walls,
    draw_day_night,
    draw_ui,
    draw_inventory_screen,
    draw_perk_menu,
    draw_quest_log,
    draw_home_interior,
    draw_bar_interior,
    draw_forest_area,
    draw_sky,
    draw_npc,
)
import settings
from settings import (
    MAP_WIDTH,
    MAP_HEIGHT,
    PLAYER_SIZE,
    PLAYER_SPEED,
    SKATEBOARD_SPEED_MULT,
    BG_COLOR,
    MINUTES_PER_FRAME,

    MUSIC_FILE,
    STEP_SOUND_FILE,
    ENTER_SOUND_FILE,
    QUEST_SOUND_FILE,
    MUSIC_VOLUME,
    SFX_VOLUME,

)

def recalc_layouts():
    """Update interior layout rects when the window size changes."""
    global HOME_WIDTH, HOME_HEIGHT, DOOR_RECT
    global BAR_WIDTH, BAR_HEIGHT, BAR_DOOR_RECT, COUNTER_RECT, BJ_RECT, SLOT_RECT, BRAWL_RECT, DART_RECT
    global FOREST_WIDTH, FOREST_HEIGHT, FOREST_DOOR_RECT

    HOME_WIDTH, HOME_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
    DOOR_RECT = pygame.Rect(HOME_WIDTH // 2 - 60, HOME_HEIGHT - 180, 120, 160)

    BAR_WIDTH, BAR_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
    BAR_DOOR_RECT = pygame.Rect(BAR_WIDTH // 2 - 60, BAR_HEIGHT - 180, 120, 160)
    COUNTER_RECT = pygame.Rect(60, BAR_HEIGHT // 2 - 60, 180, 120)
    BJ_RECT = pygame.Rect(BAR_WIDTH // 2 - 100, BAR_HEIGHT // 2 - 150, 200, 100)
    SLOT_RECT = pygame.Rect(BAR_WIDTH - 240, BAR_HEIGHT // 2 - 60, 180, 120)
    BRAWL_RECT = pygame.Rect(BAR_WIDTH // 2 - 80, 80, 160, 120)
    DART_RECT = pygame.Rect(BAR_WIDTH // 2 - 100, BAR_HEIGHT // 2 + 60, 200, 100)

    FOREST_WIDTH, FOREST_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
    FOREST_DOOR_RECT = pygame.Rect(FOREST_WIDTH // 2 - 60, FOREST_HEIGHT - 180, 120, 160)

recalc_layouts()


def compute_slot_rects():
    """Return rectangles for equipment slots based on current screen size."""
    left = settings.SCREEN_WIDTH // 10
    top = settings.SCREEN_HEIGHT // 6
    w, h = 100, 60
    spacing = 70
    return {
        "head": pygame.Rect(left, top, w, h),
        "chest": pygame.Rect(left, top + spacing, w, h),
        "arms": pygame.Rect(left, top + spacing * 2, w, h),
        "legs": pygame.Rect(left, top + spacing * 3, w, h),
        "weapon": pygame.Rect(left, top + spacing * 4, w, h),
    }


pygame.init()
pygame.mixer.init()
try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False
    print("Audio disabled: mixer could not initialize")

BUILDINGS = [
    Building(pygame.Rect(200, 150, 200, 120), "Home", "home"),
    Building(pygame.Rect(600, 300, 180, 240), "Office", "job"),
    Building(pygame.Rect(1100, 700, 300, 100), "Shop", "shop"),
    Building(pygame.Rect(400, 900, 160, 180), "Park", "park"),
    Building(pygame.Rect(460, 960, 80, 80), "Deal Spot", "dealer"),
    # Move the deal spot just outside the park so the player can reach it
    Building(pygame.Rect(580, 960, 80, 80), "Deal Spot", "dealer"),
    Building(pygame.Rect(900, 450, 220, 160), "Gym", "gym"),
    Building(pygame.Rect(1200, 250, 200, 160), "Library", "library"),
    Building(pygame.Rect(300, 600, 180, 160), "Clinic", "clinic"),
    Building(pygame.Rect(800, 750, 200, 150), "Bar", "bar"),
    Building(pygame.Rect(1400, 950, 160, 120), "Alley", "dungeon"),
    Building(pygame.Rect(1300, 550, 180, 150), "Pet Shop", "petshop"),
    Building(pygame.Rect(1000, 100, 200, 140), "Bank", "bank"),
    Building(pygame.Rect(400, 200, 200, 150), "Town Hall", "townhall"),
    Building(pygame.Rect(150, 400, 200, 150), "Workshop", "workshop"),
    Building(pygame.Rect(100, 1050, 220, 120), "Farm", "farm"),
    Building(pygame.Rect(1500, 400, 80, 100), "Woods", "forest"),
    # Expanded map locations
    Building(pygame.Rect(1800, 350, 240, 180), "Mall", "mall"),
    Building(pygame.Rect(2100, 150, 300, 200), "Suburbs", "suburbs"),
    Building(pygame.Rect(2400, 900, 260, 140), "Beach", "beach"),
]

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
    "mall": (10, 21),
    "suburbs": (0, 24),
    "beach": (6, 20),
}

SEASONS = ["Spring", "Summer", "Fall", "Winter"]
WEATHERS = ["Clear", "Rain", "Snow"]

# Simple layout for the home interior
HOME_WIDTH, HOME_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
BED_RECT = pygame.Rect(120, 160, 220, 120)
DOOR_RECT = pygame.Rect(HOME_WIDTH // 2 - 60, HOME_HEIGHT - 180, 120, 160)

# Simple quests that encourage visiting different locations
# Layout for the bar interior
BAR_WIDTH, BAR_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
BAR_DOOR_RECT = pygame.Rect(BAR_WIDTH // 2 - 60, BAR_HEIGHT - 180, 120, 160)
COUNTER_RECT = pygame.Rect(60, BAR_HEIGHT // 2 - 60, 180, 120)
BJ_RECT = pygame.Rect(BAR_WIDTH // 2 - 100, BAR_HEIGHT // 2 - 150, 200, 100)
SLOT_RECT = pygame.Rect(BAR_WIDTH - 240, BAR_HEIGHT // 2 - 60, 180, 120)
BRAWL_RECT = pygame.Rect(BAR_WIDTH // 2 - 80, 80, 160, 120)
DART_RECT = pygame.Rect(BAR_WIDTH // 2 - 100, BAR_HEIGHT // 2 + 60, 200, 100)

# Layout for the forest area with three enemies
FOREST_WIDTH, FOREST_HEIGHT = settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
FOREST_DOOR_RECT = pygame.Rect(FOREST_WIDTH // 2 - 60, FOREST_HEIGHT - 180, 120, 160)
FOREST_ENEMY_RECTS = [
    pygame.Rect(300, 300, 60, 60),
    pygame.Rect(700, 300, 60, 60),
    pygame.Rect(500, 500, 60, 60),
]


# Storyline quests completed in order
QUESTS = [
    Quest("Earn $200", lambda p: p.money >= 200),
    Quest("Reach STR 5", lambda p: p.strength >= 5),
    Quest("Reach INT 5", lambda p: p.intelligence >= 5),
    Quest("Earn $300", lambda p: p.money >= 300, next_index=1),
    Quest("Reach STR 5", lambda p: p.strength >= 5, next_index=2),
    Quest(
        "Defeat 3 alley thugs",
        lambda p: p.enemies_defeated >= 3,
        next_index=3,
    ),
    Quest(
        "Own every home upgrade",
        lambda p: set(p.home_upgrades) == {u[0] for u in HOME_UPGRADES},
        next_index=None,
    ),
]

# Simple optional side quest triggered in the new bank building
SIDE_QUEST = SideQuest(
    "Bank Delivery",
    "Deliver paperwork from the Bank to the Library",
    "library",
    lambda p: setattr(p, "money", p.money + 50),
)

# Side quest given by the wandering NPC
NPC_QUEST = SideQuest(
    "Courier Errand",
    "Deliver a package from Sam to the Gym",
    "gym",
    lambda p: setattr(p, "money", p.money + 30),
)

# Mall side quest
MALL_QUEST = SideQuest(
    "Beach Delivery",
    "Pick up sunglasses from the Mall and bring them to the Beach",
    "beach",
    lambda p: setattr(p, "money", p.money + 40),
)

NPCS = [
    NPC(pygame.Rect(500, 500, PLAYER_SIZE, PLAYER_SIZE), "Sam", NPC_QUEST),
]

# Main storyline quests progressed via story_stage
STORY_QUESTS = [
    Quest("Visit the Town Hall", lambda p: p.story_stage >= 1),
    Quest("Choose an allegiance", lambda p: p.story_stage >= 2),
    Quest("Prove your loyalty", lambda p: p.story_stage >= 3),
    Quest("Report back to your ally", lambda p: p.story_stage >= 4),
]


# Random events that may occur while exploring
def _ev_found_money(p: Player) -> None:
    p.money += 5
    bonus = 5 * p.perk_levels.get("Lucky", 0)
    p.money += 5 + bonus


def _ev_gain_int(p: Player) -> None:
    p.intelligence += 1
    p.intelligence += 1 + p.perk_levels.get("Lucky", 0)


def _ev_gain_cha(p: Player) -> None:
    p.charisma += 1
    p.charisma += 1 + p.perk_levels.get("Lucky", 0)


def _ev_trip(p: Player) -> None:
    p.health = max(p.health - 5, 0)


def _ev_theft(p: Player) -> None:
    p.money = max(p.money - 10, 0)


def _ev_free_food(p: Player) -> None:
    p.energy = min(100, p.energy + 10 + 2 * p.perk_levels.get("Lucky", 0))


def _ev_help_reward(p: Player) -> None:
    p.money += 15 + 5 * p.perk_levels.get("Lucky", 0)


def _ev_found_token(p: Player) -> None:
    p.tokens += 1


def _ev_found_metal(p: Player) -> None:
    p.resources["metal"] = p.resources.get("metal", 0) + 1


def _ev_found_cloth(p: Player) -> None:
    p.resources["cloth"] = p.resources.get("cloth", 0) + 1


def _ev_found_herb(p: Player) -> None:
    p.resources["herbs"] = p.resources.get("herbs", 0) + 1


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
]

SEASON_EVENTS = {
    "Spring": [
        Event("Flowers bloom brightly. +1 CHA", lambda p: setattr(p, "charisma", p.charisma + 1)),
    ],
    "Summer": [
        Event("Heat wave tires you out. -5 energy", lambda p: setattr(p, "energy", max(p.energy - 5, 0))),
    ],
    "Fall": [
        Event("Found $5 under fallen leaves", lambda p: setattr(p, "money", p.money + 5)),
    ],
    "Winter": [
        Event("Cold wind toughens you. +1 DEF", lambda p: setattr(p, "defense", p.defense + 1)),
    ],
}

WEATHER_EVENTS = {
    "Rain": [
        Event("Got soaked in the rain. -5 energy", lambda p: setattr(p, "energy", max(p.energy - 5, 0))),
    ],
    "Snow": [
        Event("Built a snowman for fun. +1 CHA", lambda p: setattr(p, "charisma", p.charisma + 1)),
    ],
}

LOCATION_EVENTS = {
    "beach": [
        Event("You found a seashell worth $5", lambda p: setattr(p, "money", p.money + 5)),
    ],
    "mall": [
        Event("A flash sale cost you $5", lambda p: setattr(p, "money", max(p.money - 5, 0))),
    ],
}

# Time-specific events that occur only during certain hours
TIMED_EVENTS = [
    (
        6,
        9,
        Event("You went jogging with a stranger. +1 STR", lambda p: setattr(p, "strength", p.strength + 1)),
    ),
    (
        18,
        22,
        Event("Street performer inspired you. +1 CHA", lambda p: setattr(p, "charisma", p.charisma + 1)),
    ),
    (
        20,
        24,
        Event(
            "Late-night snack stand boosted your energy", lambda p: setattr(p, "energy", min(100, p.energy + 10))
        ),
    ),
]

# Items sold at the shop: name, cost, and effect function
SHOP_ITEMS = [
    ("Cola", 3, lambda p: setattr(p, "energy", min(100, p.energy + 5))),
    ("Protein Bar", 7, lambda p: setattr(p, "health", min(100, p.health + 5))),
    ("Book", 10, lambda p: setattr(p, "intelligence", p.intelligence + 1)),
    ("Gym Pass", 15, lambda p: setattr(p, "strength", p.strength + 1)),
    ("Charm Pendant", 20, lambda p: setattr(p, "charisma", p.charisma + 1)),
    ("Skateboard", 40, lambda p: setattr(p, "has_skateboard", True)),
    ("Cola", 6, lambda p: setattr(p, "energy", min(100, p.energy + 5))),
    ("Protein Bar", 14, lambda p: setattr(p, "health", min(100, p.health + 5))),
    ("Book", 20, lambda p: setattr(p, "intelligence", p.intelligence + 1)),
    ("Gym Pass", 30, lambda p: setattr(p, "strength", p.strength + 1)),
    ("Charm Pendant", 40, lambda p: setattr(p, "charisma", p.charisma + 1)),
    ("Skateboard", 80, lambda p: setattr(p, "has_skateboard", True)),
    (
        "Leather Helmet",
        25,
        50,
        lambda p: p.inventory.append(
            InventoryItem("Leather Helmet", "head", defense=1)
        ),
    ),
    (
        "Leather Armor",
        40,
        80,
        lambda p: p.inventory.append(
            InventoryItem("Leather Armor", "chest", defense=2)
        ),
    ),
    (
        "Leather Boots",
        20,
        40,
        lambda p: p.inventory.append(
            InventoryItem("Leather Boots", "legs", defense=1, speed=1)
        ),
    ),
    (
        "Wooden Sword",
        35,
        70,
        lambda p: p.inventory.append(
            InventoryItem("Wooden Sword", "weapon", attack=2)
        ),
    ),
    (
        "Seeds x3",
        15,
        lambda p: p.resources.__setitem__(
            "seeds", p.resources.get("seeds", 0) + 3
        ),
    ),
]

# Upgrades available for purchase inside the home
HOME_UPGRADES = [
    ("Comfy Bed", 150, "Recover +20 energy when sleeping", 1),
    ("Decorations", 120, "Gain +1 CHA each morning", 1),
    ("Study Desk", 180, "Gain +1 INT each morning", 1),
    ("Small House", 1000, "Upgrade to a small house", 1),
    ("Home Gym", 250, "Gain +1 STR each morning", 2),
    ("Garden", 200, "Chance to find $10 when sleeping", 2),
    ("Mansion", 5000, "Upgrade to a mansion", 2),
    ("Arcade Room", 400, "Chance to gain a token daily", 3),
    ("Private Library", 450, "Gain +2 INT each morning", 3),
]

# Animal companions available at the Pet Shop
COMPANIONS = [
    ("Dog", 120, "DEF +1, may find $5 when you sleep"),
    ("Cat", 100, "CHA +1, 10% less walking energy"),
    ("Parrot", 150, "INT +1, may find tokens after fights"),
]

# Perks that can be unlocked with perk points
# Each perk can be upgraded up to PERK_MAX_LEVEL levels
PERK_MAX_LEVEL = 3
PERKS = [
    ("Gym Rat", "STR training gives +1 per level"),
    ("Book Worm", "INT studying gives +1 per level"),
    ("Social Butterfly", "CHA chatting gives +1 per level"),
    ("Night Owl", "Sleeping restores +10 energy per level"),
    ("Lucky", "Random events yield extra rewards"),
    ("Iron Will", "Energy costs reduced 5% per level"),
]

# Special hidden perks unlocked through achievements
SECRET_PERKS = [
    ("Bar Champion", "Win all 5 brawls"),
    ("Home Owner", "Own every home upgrade"),
    ("Perk Master", "Max out every other perk"),
]

BRAWLER_COUNT = 5

# Three unique enemies found in the forest area
FOREST_ENEMIES = [
    {"attack": 4, "defense": 1, "speed": 2, "health": 20, "reward": 30},
    {"attack": 6, "defense": 2, "speed": 3, "health": 28, "reward": 45},
    {"attack": 8, "defense": 3, "speed": 2, "health": 36, "reward": 60},
]

# Combat tweaks
DODGE_BASE = 0.1  # base dodge chance for the player
POWER_STRIKE_CHANCE = 0.25  # chance to unleash a special power strike
BLEED_TURNS = 3
BLEED_DAMAGE = 1

def buy_shop_item(player: Player, index: int) -> str:
    """Attempt to buy an item from SHOP_ITEMS by index."""
    if index < 0 or index >= len(SHOP_ITEMS):
        return "Invalid item"
    name, cost, effect = SHOP_ITEMS[index]
    if name == "Skateboard" and player.has_skateboard:
        return "Already have skateboard"
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    effect(player)
    return f"Bought {name}"

EVENT_CHANCE = 0.0008  # roughly once every ~20s at 60 FPS

def buy_home_upgrade(player: Player, index: int) -> str:
    """Attempt to purchase a home upgrade by index."""
    if index < 0 or index >= len(HOME_UPGRADES):
        return "Invalid upgrade"
    name, cost, _, req = HOME_UPGRADES[index]
    if req > player.home_level:
        return "Locked"
    if name in player.home_upgrades:
        return "Already owned"
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    player.home_upgrades.append(name)
    if name == "Small House":
        player.home_level = 2
    elif name == "Mansion":
        player.home_level = 3
    return f"Bought {name}"


def available_home_upgrades(player: Player):
    """Return a list of upgrades unlocked for the player's house level."""
    return [u for u in HOME_UPGRADES if u[3] <= player.home_level]


def bank_deposit(player: Player, amount: int = 10) -> str:
    """Deposit money into the bank."""
    if player.money < amount:
        return "Need $10"
    player.money -= amount
    player.bank_balance += amount
    return f"Deposited ${amount}"


def bank_withdraw(player: Player, amount: int = 10) -> str:
    """Withdraw money from the bank."""
    if player.bank_balance < amount:
        return "No funds"
    player.bank_balance -= amount
    player.money += amount
    return f"Withdrew ${amount}"


def adopt_companion(player: Player, index: int) -> str:
    """Adopt a pet companion by index."""
    if index < 0 or index >= len(COMPANIONS):
        return "Invalid choice"
    name, cost, _desc = COMPANIONS[index]
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    player.companion = name
    if name == "Dog":
        player.defense += 1
    elif name == "Cat":
        player.charisma += 1
    elif name == "Parrot":
        player.intelligence += 1
    return f"Adopted {name}!"


def plant_seed(player: Player) -> str:
    """Plant a seed at the farm if available."""
    if player.resources.get("seeds", 0) <= 0:
        return "No seeds"
    player.resources["seeds"] -= 1
    player.crops.append(player.day)
    return "Seed planted"


def harvest_crops(player: Player) -> str:
    """Harvest any crops that have grown for 3 days."""
    ready = [d for d in player.crops if player.day - d >= 3]
    if not ready:
        return "Nothing ready"
    for d in ready:
        player.crops.remove(d)
        player.money += 15
    return f"Harvested {len(ready)} crops"

EVENT_CHANCE = 0.0004  # less frequent random events

SAVE_FILE = "savegame.json"
LEADERBOARD_FILE = "leaderboard.json"



def building_open(btype, minutes, player: Player):
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
    return True



def check_quests(player):
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


def energy_cost(player: Player, base: float) -> float:
    """Return energy cost adjusted by Iron Will and hidden perks."""
    level = player.perk_levels.get("Iron Will", 0)
    cost = base * (1 - 0.05 * level)
    if player.perk_levels.get("Perk Master"):
        cost *= 0.9
    return cost


def update_weather(player: Player) -> None:
    """Update season and daily weather."""
    season_index = ((player.day - 1) // 30) % len(SEASONS)
    player.season = SEASONS[season_index]
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
    """Increment the day counter and apply bank interest."""
    player.day += 1
    update_weather(player)
    interest = int(player.bank_balance * 0.01)
    player.bank_balance += interest
    return interest


def sleep(player: Player) -> str | None:
    """Restore energy and apply home and perk bonuses."""
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
    messages = []
    if player.companion == "Dog" and random.random() < 0.2:
        player.money += 5
        messages.append("Your dog brought you $5!")
    if "Garden" in player.home_upgrades and random.random() < 0.3:
        player.money += 10
        messages.append("Found $10 in the garden")
    if "Arcade Room" in player.home_upgrades and random.random() < 0.3:
        player.tokens += 1
        messages.append("Won a token in your arcade")
    if interest:
        messages.append(f"Earned ${interest} interest")
    return " ".join(messages) if messages else None


def check_hidden_perks(player: Player) -> str | None:
    """Unlock secret perks when requirements are met."""
    if (
        player.brawls_won >= BRAWLER_COUNT
        and "Bar Champion" not in player.perk_levels
    ):
        player.perk_levels["Bar Champion"] = 1
        return "Secret perk unlocked: Bar Champion!"
    if (
        set(player.home_upgrades) == {u[0] for u in HOME_UPGRADES}
        and "Home Owner" not in player.perk_levels
    ):
        player.perk_levels["Home Owner"] = 1
        return "Secret perk unlocked: Home Owner!"
    if (
        all(player.perk_levels.get(name, 0) >= PERK_MAX_LEVEL for name, _ in PERKS)
        and "Perk Master" not in player.perk_levels
    ):
        player.perk_levels["Perk Master"] = 1
        return "Secret perk unlocked: Perk Master!"
    return None


def update_leaderboard(player: Player) -> None:
    """Record story completion time and money in the leaderboard file."""
    record = {"day": player.day, "money": int(player.money)}
    board = []
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


def check_achievements(player: Player) -> str | None:
    """Unlock achievements when goals are met."""
    if "First Blood" not in player.achievements and player.enemies_defeated >= 1:
        player.achievements.append("First Blood")
        return "Achievement unlocked: First Blood!"
    if (
        "Brawler Master" not in player.achievements
        and player.brawls_won >= BRAWLER_COUNT
    ):
        player.achievements.append("Brawler Master")
        return "Achievement unlocked: Brawler Master!"
    if "Wealthy" not in player.achievements and player.money >= 1000:
        player.achievements.append("Wealthy")
        return "Achievement unlocked: Wealthy!"
    if (
        "Story Hero" not in player.achievements
        and all(q.completed for q in STORY_QUESTS)
    ):
        player.achievements.append("Story Hero")
        update_leaderboard(player)
        return "Achievement unlocked: Story Hero!"
    return None


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
            dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            rect = npc.rect.move(dx * 4, dy * 4)
            if 0 <= rect.x <= MAP_WIDTH - PLAYER_SIZE and 0 <= rect.y <= MAP_HEIGHT - PLAYER_SIZE:
                collision = False
                for b in BUILDINGS:
                    if rect.colliderect(b.rect):
                        collision = True
                        break
                if not collision:
                    npc.rect = rect


def advance_story(player: Player) -> None:
    """Update story stage based on branch objectives."""
    if player.story_branch == "mayor" and player.story_stage == 2:
        if player.enemies_defeated >= 3:
            player.story_stage = 3
    if player.story_branch == "gang" and player.story_stage == 2:
        if player.gang_package_done:
            player.story_stage = 3


def check_story(player: Player) -> bool:
    """Mark story quests completed based on story_stage."""
    changed = False
    for i, q in enumerate(STORY_QUESTS):
        if not q.completed and q.check(player):
            q.completed = True
            changed = True
    return changed


def play_blackjack(player: Player) -> str:
    if player.tokens < 1:
        return "No tokens left!"
    player.tokens -= 1
    player_score = random.randint(16, 23)
    dealer_score = random.randint(16, 23)
    if player_score > 21:
        return "Bust!"
    if dealer_score > 21 or player_score > dealer_score:
        player.tokens += 2
        return "You win! +2 tokens"
    if player_score == dealer_score:
        player.tokens += 1
        return "Push. Token returned"
    return "Dealer wins"


def play_slots(player: Player) -> str:
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


def play_darts(player: Player) -> str:
    """Simple skill game that can win tokens."""
    if player.tokens < 1:
        return "No tokens left!"
    player.tokens -= 1
    score = random.randint(1, 20) + player.speed // 2
    if score >= 20:
        player.tokens += 2
        return "Bullseye! +2 tokens"
    if score >= 15:
        player.tokens += 1
        return "Nice shot! +1 token"
    return "Missed the board"


def go_fishing(player: Player) -> str:
    """Fish at the park for cash or materials."""
    if player.energy < 5:
        return "Too tired to fish!"
    player.energy -= energy_cost(player, 5)
    if random.random() < 0.3:
        return "Nothing was biting"
    if random.random() < 0.2:
        player.resources["herbs"] = player.resources.get("herbs", 0) + 1
        return "Found some herbs by the water"
    reward = random.randint(5, 20)
    player.money += reward
    return f"Caught a fish! +${reward}"


def solve_puzzle(player: Player) -> str:
    """Solve a puzzle at the library for a reward."""
    if player.energy < 5:
        return "Too tired to think!"
    player.energy -= energy_cost(player, 5)
    chance = player.intelligence + random.randint(0, 10)
    if chance > 12:
        reward = random.randint(10, 20)
        player.money += reward
        return f"Puzzle solved! +${reward}"
    return "Couldn't solve it"


def _combat_stats(player: Player):
    atk = player.strength
    df = player.defense
    spd = player.speed
    if player.perk_levels.get("Bar Champion"):
        atk += 2
    if player.companion == "Dog":
        df += 1
    for item in player.equipment.values():
        if item:
            atk += item.attack
            df += item.defense
            spd += item.speed
    return atk, df, spd



def fight_brawler(player: Player) -> str:
    if player.brawls_won >= BRAWLER_COUNT:
        return "No challengers remain"
    if player.energy < 10:
        return "Too tired to fight!"
    player.energy -= 10
    player.energy -= energy_cost(player, 10)

    stage = player.brawls_won + 1
    enemy = {
        "attack": random.randint(3 + stage, 6 + stage * 2),
        "defense": random.randint(1 + stage, 3 + stage),
        "speed": random.randint(1 + stage // 2, 5 + stage // 2),
        "health": 20 + stage * 10,
    }
    p_atk, p_def, p_spd = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            dmg = max(1, p_atk - enemy["defense"])
            if not special_used and random.random() < POWER_STRIKE_CHANCE:
                dmg *= 2
                bleed_turns = BLEED_TURNS
                special_used = True
            e_hp -= dmg
        else:
            if random.random() < (DODGE_BASE + player.speed * 0.02):
                pass  # dodged
            else:
                dmg = max(1, enemy["attack"] - p_def)
                p_hp -= dmg
        turn_player = not turn_player
        if bleed_turns > 0:
            e_hp -= BLEED_DAMAGE
            bleed_turns -= 1
    player.health = max(p_hp, 0)
    if p_hp <= 0:
        return "You lost the fight!"
    reward = 20 + stage * 10
    player.money += reward
    player.brawls_won += 1
    msg = f"You won the fight {stage}! +${reward}"
    if player.brawls_won == BRAWLER_COUNT:
        msg += " All brawlers defeated!"
    return msg
def fight_enemy(player: Player) -> str:
    """Fight a random street enemy in the alley."""
    if player.energy < 10:
        return "Too tired to fight!"
    player.energy -= energy_cost(player, 10)

    scale = 1 + player.enemies_defeated // 5
    enemy = {
        "attack": random.randint(2 * scale, 4 * scale),
        "defense": random.randint(1 * scale, 3 * scale),
        "speed": random.randint(1, 4),
        "health": 15 + 5 * scale,
    }
    p_atk, p_def, p_spd = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            dmg = max(1, p_atk - enemy["defense"])
            if not special_used and random.random() < POWER_STRIKE_CHANCE:
                dmg *= 2
                bleed_turns = BLEED_TURNS
                special_used = True
            e_hp -= dmg
        else:
            if random.random() < (DODGE_BASE + player.speed * 0.02):
                pass
            else:
                dmg = max(1, enemy["attack"] - p_def)
                p_hp -= dmg
        turn_player = not turn_player
        if bleed_turns > 0:
            e_hp -= BLEED_DAMAGE
            bleed_turns -= 1
    player.health = max(p_hp, 0)
    if p_hp <= 0:
        return "You lost the fight!"

    cash = random.randint(5, 25)
    player.money += cash
    loot = ""
    if random.random() < 0.3:
        player.tokens += 1
        loot = " and found a token"
    if random.random() < 0.4:
        res = random.choice(["metal", "cloth", "herbs"])
        player.resources[res] = player.resources.get(res, 0) + 1
        loot += f" +1 {res}"
    if player.companion == "Parrot" and random.random() < 0.3:
        player.tokens += 1
        loot += " (parrot found another)"
    player.enemies_defeated += 1
    return f"Enemy defeated! +${cash}{loot}"


def fight_forest_enemy(player: Player, index: int) -> str:
    """Fight one of the fixed forest enemies by index."""
    if index < 0 or index >= len(FOREST_ENEMIES):
        return "Invalid enemy"
    if player.energy < 10:
        return "Too tired to fight!"
    player.energy -= energy_cost(player, 10)

    enemy = FOREST_ENEMIES[index]
    p_atk, p_def, p_spd = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            dmg = max(1, p_atk - enemy["defense"])
            if not special_used and random.random() < POWER_STRIKE_CHANCE:
                dmg *= 2
                bleed_turns = BLEED_TURNS
                special_used = True
            e_hp -= dmg
        else:
            if random.random() < (DODGE_BASE + player.speed * 0.02):
                pass
            else:
                dmg = max(1, enemy["attack"] - p_def)
                p_hp -= dmg
        turn_player = not turn_player
        if bleed_turns > 0:
            e_hp -= BLEED_DAMAGE
            bleed_turns -= 1
    player.health = max(p_hp, 0)
    if p_hp <= 0:
        return "You lost the fight!"

    player.money += enemy["reward"]
    loot = ""
    if random.random() < 0.5:
        res = random.choice(["metal", "cloth", "herbs"])
        player.resources[res] = player.resources.get(res, 0) + 1
        loot = f" +1 {res}"
    player.enemies_defeated += 1
    return f"Enemy defeated! +${enemy['reward']}{loot}"



def save_game(player):
    data = {
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
        "tokens": player.tokens,

        "brawls_won": player.brawls_won,
        "enemies_defeated": player.enemies_defeated,

        "companion": player.companion,

        "has_skateboard": player.has_skateboard,
        "home_upgrades": player.home_upgrades,
        "home_level": player.home_level,
        "bank_balance": player.bank_balance,
        "perk_points": player.perk_points,
        "perk_levels": player.perk_levels,
        "next_strength_perk": player.next_strength_perk,
        "next_intelligence_perk": player.next_intelligence_perk,
        "next_charisma_perk": player.next_charisma_perk,
        "current_quest": player.current_quest,
        "enemies_defeated": player.enemies_defeated,
        "inventory": [item.__dict__ for item in player.inventory],
        "equipment": {
            slot: (it.__dict__ if it else None) for slot, it in player.equipment.items()
        },

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
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE) as f:
        data = json.load(f)
    player = Player(
        pygame.Rect(
            data.get("x", MAP_WIDTH // 2),
            data.get("y", MAP_HEIGHT // 2),
            PLAYER_SIZE,
            PLAYER_SIZE,
        )
    )
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
    player.dealer_level = data.get("dealer_level", player.dealer_level)
    player.dealer_shifts = data.get("dealer_shifts", player.dealer_shifts)
    player.clinic_level = data.get("clinic_level", player.clinic_level)
    player.clinic_shifts = data.get("clinic_shifts", player.clinic_shifts)
    player.tokens = data.get("tokens", player.tokens)
    player.brawls_won = data.get("brawls_won", 0)
    player.enemies_defeated = data.get("enemies_defeated", 0)

    player.has_skateboard = data.get("has_skateboard", player.has_skateboard)
    player.home_upgrades = data.get("home_upgrades", [])
    player.home_level = data.get("home_level", 1)
    player.bank_balance = data.get("bank_balance", 0.0)
    player.perk_points = data.get("perk_points", 0)
    player.perk_levels = data.get("perk_levels", {})
    player.next_strength_perk = data.get("next_strength_perk", 5)
    player.next_intelligence_perk = data.get("next_intelligence_perk", 5)
    player.next_charisma_perk = data.get("next_charisma_perk", 5)
    player.current_quest = data.get("current_quest", 0)
    player.enemies_defeated = data.get("enemies_defeated", 0)
    player.companion = data.get("companion")
    player.npc_progress = data.get("npc_progress", {})
    player.story_stage = data.get("story_stage", 0)
    player.story_branch = data.get("story_branch")
    player.gang_package_done = data.get("gang_package_done", False)
    player.resources = data.get(
        "resources", {"metal": 0, "cloth": 0, "herbs": 0, "seeds": 0}
    )
    player.crops = data.get("crops", [])
    player.season = data.get("season", "Spring")
    player.weather = data.get("weather", "Clear")
    player.achievements = data.get("achievements", [])
    for item in data.get("inventory", []):
        player.inventory.append(InventoryItem(**item))
    for slot, item in data.get("equipment", {}).items():
        if item:
            player.equipment[slot] = InventoryItem(**item)

    for completed, q in zip(data.get("quests", []), QUESTS):
        q.completed = completed
    return player


def start_menu(screen, font):
    """Display a simple start menu and return True if load selected."""
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
        screen.blit(start_txt, (settings.SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 320))
        screen.blit(load_txt, (settings.SCREEN_WIDTH // 2 - load_txt.get_width() // 2, 360))
        if board:
            lb_title = font.render("Top Completions", True, (230, 230, 230))
            screen.blit(lb_title, (settings.SCREEN_WIDTH // 2 - lb_title.get_width() // 2, 400))
            for i, rec in enumerate(board):
                txt = font.render(
                    f"{i+1}. Day {rec['day']} - ${rec['money']}", True, (200, 200, 200)
                )
                screen.blit(txt, (settings.SCREEN_WIDTH // 2 - txt.get_width() // 2, 420 + i * 20))
        pygame.display.flip()
        pygame.time.wait(20)


def main():
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    if start_menu(screen, font):
        loaded = load_game()
    else:
        loaded = None

    step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
    enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
    quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
    for snd in (step_sound, enter_sound, quest_sound):
        snd.set_volume(SFX_VOLUME)
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(-1)
    if SOUND_ENABLED:
        step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
        enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
        quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
        for snd in (step_sound, enter_sound, quest_sound):
            snd.set_volume(SFX_VOLUME)
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    else:
        step_sound = enter_sound = quest_sound = None

    load_player_sprites()

    player = Player(pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE))
    loaded_player = loaded
    shop_message = ""
    if loaded_player:
        player = loaded_player
        update_weather(player)
        shop_message = "Game loaded!"
        shop_message_timer = 60
    else:
        update_weather(player)
        shop_message_timer = 0
    in_building = None
    frame = 0
    show_inventory = False
    show_perk_menu = False
    show_log = False
    inside_home = False
    inside_bar = False
    inside_forest = False
    home_return = (0, 0)
    bar_return = (0, 0)
    forest_return = (0, 0)
    dragging_item = None
    drag_origin = None
    drag_pos = (0, 0)
    slot_rects = compute_slot_rects()

    while True:
        frame += 1
        player.time += MINUTES_PER_FRAME
        if player.time >= 1440:
            player.time -= 1440
            advance_day(player)
        update_npcs()
        advance_story(player)
        check_story(player)
        if check_perk_unlocks(player):
            shop_message = "Gained a perk point! Press P to spend"
            shop_message_timer = 90
        secret = check_hidden_perks(player)
        if secret:
            shop_message = secret
            shop_message_timer = 90
        achieve = check_achievements(player)
        if achieve:
            shop_message = achieve
            shop_message_timer = 90
        item_rects = []
        if show_inventory:
            for i, item in enumerate(player.inventory):
                col = i % 5
                row = i // 5
                item_rects.append(
                    (pygame.Rect(320 + col * 120, 150 + row * 70, 100, 60), item)
                )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    save_game(player)
                    shop_message = "Game saved!"
                    shop_message_timer = 60
                elif event.key == pygame.K_F9:
                    loaded = load_game()
                    if loaded:
                        player = loaded
                        shop_message = "Game loaded!"
                    else:
                        shop_message = "No save found!"
                    shop_message_timer = 60
                elif event.key == pygame.K_i:
                    show_inventory = not show_inventory
                    dragging_item = None
                elif event.key == pygame.K_p and player.perk_points > 0:
                    show_perk_menu = not show_perk_menu
                    dragging_item = None
                elif event.key == pygame.K_l:
                    show_log = not show_log
                    dragging_item = None
                elif event.key == pygame.K_h and not show_inventory and not show_log and not in_building:
                    pot = next((i for i in player.inventory if i.name == "Health Potion"), None)
                    if pot:
                        player.inventory.remove(pot)
                        player.health = min(100, player.health + 30)
                        shop_message = "Drank Health Potion (+30 HP)"
                    else:
                        shop_message = "No potion"
                    shop_message_timer = 60
                elif event.key == pygame.K_t and not in_building and not show_inventory and not show_log:
                    player.time += 180
                    if player.time >= 1440:
                        player.time -= 1440
                        advance_day(player)
                    shop_message = "Skipped ahead 3 hours"
                    shop_message_timer = 60
            if show_inventory:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    handled = False
                    for i, (rect, item) in enumerate(item_rects):
                        if rect.collidepoint(pos):
                            dragging_item = item
                            drag_origin = ('inventory', i)
                            drag_pos = pos
                            player.inventory.pop(i)
                            handled = True
                            break
                    if not handled:
                        for slot, rect in slot_rects.items():
                            if rect.collidepoint(pos) and player.equipment.get(slot):
                                dragging_item = player.equipment[slot]
                                drag_origin = ('slot', slot)
                                drag_pos = pos
                                player.equipment[slot] = None
                                break
                elif event.type == pygame.MOUSEMOTION and dragging_item:
                    drag_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging_item:
                    pos = event.pos
                    placed = False
                    for slot, rect in slot_rects.items():
                        if rect.collidepoint(pos) and dragging_item.slot == slot and player.equipment.get(slot) is None:
                            player.equipment[slot] = dragging_item
                            placed = True
                            break
                    if not placed:
                        player.inventory.append(dragging_item)
                    dragging_item = None
            if show_perk_menu and event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(PERKS):
                        name = PERKS[idx][0]
                        level = player.perk_levels.get(name, 0)
                        if level < PERK_MAX_LEVEL and player.perk_points > 0:
                            player.perk_levels[name] = level + 1
                            player.perk_points -= 1
                            shop_message = f"Perk upgraded: {name} Lv{level+1}"
                            shop_message_timer = 90
                        else:
                            shop_message = "Perk at max level"
                            shop_message_timer = 60
                    show_perk_menu = False
                elif event.key in (pygame.K_q, pygame.K_p):
                    show_perk_menu = False
            if show_log and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_l, pygame.K_q):
                    show_log = False
            if event.type == pygame.KEYDOWN and inside_home:
                if event.key == pygame.K_e:
                    if player.rect.colliderect(BED_RECT):
                        extra = sleep(player)
                        shop_message = "You slept. New day!"
                        if extra:
                            shop_message += " " + extra
                        shop_message_timer = 60
                    elif player.rect.colliderect(DOOR_RECT):
                        inside_home = False
                        player.rect.topleft = home_return
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    avail = [u for u in HOME_UPGRADES if u[3] <= player.home_level]
                    idx = event.key - pygame.K_1
                    if idx < len(avail):
                        full_idx = HOME_UPGRADES.index(avail[idx])
                        shop_message = buy_home_upgrade(player, full_idx)
                    else:
                        shop_message = "Invalid choice"
                    shop_message_timer = 60

            if event.type == pygame.KEYDOWN and inside_bar:
                if event.key == pygame.K_e:
                    if (
                        player.story_branch == "gang"
                        and player.side_quest == "Gang Package"
                        and player.rect.colliderect(COUNTER_RECT)
                    ):
                        player.side_quest = None
                        player.gang_package_done = True
                        shop_message = "You delivered the package"
                        shop_message_timer = 60
                        continue
                    if (
                        player.story_branch == "gang"
                        and player.story_stage == 3
                        and player.rect.colliderect(COUNTER_RECT)
                    ):
                        player.story_stage = 4
                        shop_message = "Gang Leader: Nice work"
                        shop_message_timer = 60
                        continue
                    if player.rect.colliderect(COUNTER_RECT):
                        if player.money >= 10:
                            player.money -= 10
                            player.tokens += 1
                            shop_message = "Bought a token"
                        else:
                            shop_message = "Need $10"
                    elif player.rect.colliderect(BJ_RECT):
                        shop_message = play_blackjack(player)
                    elif player.rect.colliderect(SLOT_RECT):
                        shop_message = play_slots(player)
                    elif player.rect.colliderect(DART_RECT):
                        shop_message = play_darts(player)
                    elif player.rect.colliderect(BRAWL_RECT):
                        shop_message = fight_brawler(player)
                    elif player.rect.colliderect(BAR_DOOR_RECT):
                        inside_bar = False
                        player.rect.topleft = bar_return
                    else:
                        shop_message = ""
                    shop_message_timer = 60

            if event.type == pygame.KEYDOWN and inside_forest:
                if event.key == pygame.K_e:
                    for i, rect in enumerate(FOREST_ENEMY_RECTS):
                        if player.rect.colliderect(rect):
                            shop_message = fight_forest_enemy(player, i)
                            break
                    else:
                        if player.rect.colliderect(FOREST_DOOR_RECT):
                            inside_forest = False
                            player.rect.topleft = forest_return
                    shop_message_timer = 60

            if event.type == pygame.KEYDOWN and in_building:
                if in_building == "job" and event.key == pygame.K_e:
                    if player.energy >= 20:
                        pay = 30 + 20 * (player.office_level - 1)
                        pay = 20 + 15 * (player.office_level - 1)
                        player.money += pay
                        player.energy -= 20
                        player.energy -= energy_cost(player, 20)
                        player.office_shifts += 1
                        if (
                            player.office_shifts >= 10
                            and player.intelligence >= 5 * player.office_level
                            and player.charisma >= 5 * player.office_level
                        ):
                            player.office_level += 1
                            player.office_shifts = 0
                            shop_message = (
                                f"You were promoted! Office level {player.office_level}"
                            )
                        else:
                            shop_message = f"You worked! +${pay}, -20 energy"
                    else:
                        shop_message = "Too tired to work!"
                    shop_message_timer = 60
                elif in_building == "home":
                    player.energy = 100
                    player.time = 8 * 60
                    player.day += 1
                    shop_message = "You slept. New day!"
                    shop_message_timer = 60
                    if event.key == pygame.K_e:
                        extra = sleep(player)
                        shop_message = "You slept. New day!"
                        if extra:
                            shop_message += " " + extra
                        shop_message_timer = 60
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        shop_message = buy_home_upgrade(player, idx)
                        shop_message_timer = 60
                    else:
                        continue
                elif in_building == "shop":
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        shop_message = buy_shop_item(player, idx)
                        shop_message_timer = 60
                    elif event.key == pygame.K_0:
                        shop_message = buy_shop_item(player, 9)
                        shop_message_timer = 60
                    elif event.key == pygame.K_e:
                        shop_message = "Press number keys to buy"
                        shop_message_timer = 60
                    else:
                        continue
                elif in_building == "gym" and event.key == pygame.K_e:
                    if player.side_quest == NPC_QUEST.name:
                        NPC_QUEST.reward(player)
                        player.side_quest = None
                        shop_message = "Delivered the package!"
                    elif player.money >= 10 and player.energy >= 10:
                        player.money -= 10
                        player.energy -= 10
                        player.energy -= energy_cost(player, 10)
                        player.health = min(player.health + 5, 100)
                        player.strength += 1
                        shop_message = "You worked out! +1 STR, +5 health"
                        bonus = player.perk_levels.get("Gym Rat", 0)
                        gain = 1 + bonus
                        player.strength += gain
                        msg_gain = f" +{gain} STR"
                        shop_message = "You worked out!" + msg_gain + ", +5 health"
                    elif player.money < 10:
                        shop_message = "Need $10 to train"
                    else:
                        shop_message = "Too tired to train!"
                    shop_message_timer = 60
                elif in_building == "library" and event.key == pygame.K_e:
                    if player.money >= 5 and player.energy >= 5:
                        player.money -= 5
                        player.energy -= 5
                        player.intelligence += 1
                        shop_message = "You studied! +1 INT"
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Book Worm", 0)
                        gain = 1 + bonus
                        player.intelligence += gain
                        msg_gain = f" +{gain} INT"
                        shop_message = "You studied!" + msg_gain
                        if player.side_quest == SIDE_QUEST.name:
                            SIDE_QUEST.reward(player)
                            player.side_quest = None
                            shop_message += " and delivered the papers"
                    elif player.money < 5:
                        shop_message = "Need $5 to study"
                    else:
                        shop_message = "Too tired to study!"
                    shop_message_timer = 60
                elif in_building == "library" and event.key == pygame.K_p:
                    shop_message = solve_puzzle(player)
                    shop_message_timer = 60
                elif in_building == "park" and event.key == pygame.K_e:
                    if player.energy >= 5:
                        player.energy -= 5
                        player.charisma += 1
                        shop_message = "You socialized! +1 CHA"
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Social Butterfly", 0)
                        gain = 1 + bonus
                        player.charisma += gain
                        msg_gain = f" +{gain} CHA"
                        shop_message = "You socialized!" + msg_gain
                    else:
                        shop_message = "Too tired to chat!"
                    shop_message_timer = 60
                elif in_building == "park" and event.key == pygame.K_f:
                    shop_message = go_fishing(player)
                    shop_message_timer = 60
                elif in_building == "bar":
                    if event.key == pygame.K_b:
                        if player.money >= 10:
                            player.money -= 10
                            player.tokens += 1
                            shop_message = "Bought a token"
                        else:
                            shop_message = "Need $10" 
                            shop_message = "Need $10"
                    elif event.key == pygame.K_j:
                        shop_message = play_blackjack(player)
                    elif event.key == pygame.K_s:
                        shop_message = play_slots(player)
                    elif event.key == pygame.K_d:
                        shop_message = play_darts(player)
                    elif event.key == pygame.K_f:
                        shop_message = fight_brawler(player)
                    elif event.key == pygame.K_e:
                        shop_message = "Buy tokens with B"  # hint when pressing E
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "dungeon" and event.key == pygame.K_e:
                    shop_message = fight_enemy(player)
                    shop_message_timer = 60
                elif in_building == "forest" and event.key == pygame.K_e:
                    # fallback if player enters the woods via in_building
                    shop_message = fight_forest_enemy(player, random.randrange(3))
                    shop_message_timer = 60
                elif in_building == "petshop" and pygame.K_1 <= event.key <= pygame.K_3:
                    idx = event.key - pygame.K_1
                    shop_message = adopt_companion(player, idx)
                    shop_message_timer = 60
                elif in_building == "bank":
                    if event.key == pygame.K_e:
                        if not player.side_quest:
                            player.side_quest = SIDE_QUEST.name
                            shop_message = "Accepted delivery job!"
                        else:
                            shop_message = "Talk to the librarian to finish"
                    elif event.key == pygame.K_d:
                        shop_message = bank_deposit(player)
                    elif event.key == pygame.K_w:
                        shop_message = bank_withdraw(player)
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "workshop":
                    if event.key == pygame.K_1:
                        if player.resources.get("herbs", 0) >= 2:
                            player.resources["herbs"] -= 2
                            player.inventory.append(
                                InventoryItem("Health Potion", "consumable")
                            )
                            shop_message = "Crafted Health Potion"
                        else:
                            shop_message = "Need 2 herbs"
                    elif event.key == pygame.K_2:
                        if player.resources.get("metal", 0) >= 3:
                            player.resources["metal"] -= 3
                            player.inventory.append(
                                InventoryItem(
                                    "Iron Sword",
                                    "weapon",
                                    attack=4,
                                )
                            )
                            shop_message = "Forged Iron Sword"
                        else:
                            shop_message = "Need 3 metal"
                    elif event.key == pygame.K_3:
                        weapon = player.equipment.get("weapon")
                        if weapon and player.resources.get("metal", 0) >= 2:
                            player.resources["metal"] -= 2
                            weapon.attack += 1
                            weapon.level += 1
                            shop_message = "Upgraded weapon"
                        else:
                            shop_message = "Need weapon & 2 metal"
                    elif event.key == pygame.K_4:
                        armor = player.equipment.get("chest")
                        if armor and player.resources.get("cloth", 0) >= 2:
                            player.resources["cloth"] -= 2
                            armor.defense += 1
                            armor.level += 1
                            shop_message = "Upgraded armor"
                        else:
                            shop_message = "Need armor & 2 cloth"
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "farm":
                    if event.key == pygame.K_p:
                        shop_message = plant_seed(player)
                    elif event.key == pygame.K_h:
                        shop_message = harvest_crops(player)
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "mall" and event.key == pygame.K_e:
                    if not player.side_quest:
                        player.side_quest = MALL_QUEST.name
                        shop_message = "Picked up sunglasses order"
                    else:
                        shop_message = "Finish your current job first"
                    shop_message_timer = 60
                elif in_building == "beach" and event.key == pygame.K_e:
                    if player.side_quest == MALL_QUEST.name:
                        MALL_QUEST.reward(player)
                        player.side_quest = None
                        shop_message = "Delivered sunglasses!"
                    elif player.energy >= 5:
                        player.energy -= energy_cost(player, 5)
                        player.charisma += 1
                        shop_message = "Relaxed on the beach"
                    else:
                        shop_message = "Too tired to relax!"
                    shop_message_timer = 60
                elif in_building == "suburbs" and event.key == pygame.K_e:
                    if player.energy >= 5:
                        player.energy -= energy_cost(player, 5)
                        player.money += 5
                        shop_message = "Helped a neighbor! +$5"
                    else:
                        shop_message = "Too tired to help"
                    shop_message_timer = 60
                elif in_building == "townhall":
                    if player.story_stage == 0 and event.key == pygame.K_e:
                        player.story_stage = 1
                        shop_message = "Mayor: Help clean up the city? Y/N"
                    elif player.story_stage == 1 and event.key == pygame.K_y:
                        player.story_branch = "mayor"
                        player.story_stage = 2
                        shop_message = "Mayor: Defeat 3 thugs in the alley."
                    elif player.story_stage == 1 and event.key == pygame.K_n:
                        player.story_branch = "gang"
                        player.story_stage = 2
                        player.side_quest = "Gang Package"
                        shop_message = "A shady figure gives you a package."
                    elif (
                        player.story_branch == "mayor"
                        and player.story_stage == 3
                        and event.key == pygame.K_e
                    ):
                        player.story_stage = 4
                        shop_message = "Mayor: Thank you for your help!"
                    else:
                        continue
                    shop_message_timer = 90
                elif in_building == "dealer" and event.key == pygame.K_e:
                    if player.energy >= 20:
                        pay = 50 + 25 * (player.dealer_level - 1)
                        pay = 40 + 20 * (player.dealer_level - 1)
                        player.money += pay
                        player.energy -= 20
                        player.energy -= energy_cost(player, 20)
                        player.dealer_shifts += 1
                        if (
                            player.dealer_shifts >= 10
                            and player.strength >= 5 * player.dealer_level
                            and player.charisma >= 5 * player.dealer_level
                        ):
                            player.dealer_level += 1
                            player.dealer_shifts = 0
                            shop_message = f"You were promoted! Dealer level {player.dealer_level}"
                        else:
                            shop_message = f"You dealt! +${pay}, -20 energy"
                    else:
                        shop_message = "Too tired to deal!"
                    shop_message_timer = 60
                elif in_building == "clinic" and event.key == pygame.K_e:
                    if player.energy >= 20:
                        pay = 40 + 20 * (player.clinic_level - 1)
                        pay = 30 + 15 * (player.clinic_level - 1)
                        player.money += pay
                        player.energy -= 20
                        player.energy -= energy_cost(player, 20)
                        player.clinic_shifts += 1
                        if (
                            player.clinic_shifts >= 10
                            and player.intelligence >= 5 * player.clinic_level
                            and player.strength >= 5 * player.clinic_level
                        ):
                            player.clinic_level += 1
                            player.clinic_shifts = 0
                            shop_message = f"You were promoted! Clinic level {player.clinic_level}"
                        else:
                            shop_message = f"You treated patients! +${pay}, -20 energy"
                    else:
                        shop_message = "Too tired to work here!"
                    shop_message_timer = 60

        dx = dy = 0
        keys = pygame.key.get_pressed()
        speed = PLAYER_SPEED
        if player.has_skateboard and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            speed = int(PLAYER_SPEED * SKATEBOARD_SPEED_MULT)
        if inside_home and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed

            next_rect = player.rect.move(dx, dy)
            if 40 <= next_rect.x <= HOME_WIDTH - PLAYER_SIZE - 40 and 40 <= next_rect.y <= HOME_HEIGHT - PLAYER_SIZE - 40:
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif inside_bar and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed

            next_rect = player.rect.move(dx, dy)
            if 40 <= next_rect.x <= BAR_WIDTH - PLAYER_SIZE - 40 and 40 <= next_rect.y <= BAR_HEIGHT - PLAYER_SIZE - 40:
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif inside_forest and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed

            next_rect = player.rect.move(dx, dy)
            if 40 <= next_rect.x <= FOREST_WIDTH - PLAYER_SIZE - 40 and 40 <= next_rect.y <= FOREST_HEIGHT - PLAYER_SIZE - 40:
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif not in_building and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed

            next_rect = player.rect.move(dx, dy)
            if 0 <= next_rect.x <= MAP_WIDTH - PLAYER_SIZE and 0 <= next_rect.y <= MAP_HEIGHT - PLAYER_SIZE:
                collision = False
                for b in BUILDINGS:
                    overlap = next_rect.clip(b.rect)
                    if overlap.width > 8 and overlap.height > 8:
                        collision = True
                        break
                if not collision:
                    if dx != 0 or dy != 0:
                        if frame % 12 == 0 and SOUND_ENABLED:
                            step_sound.play()
                        player.energy = max(player.energy - 0.04, 0)
                        cost_mult = 1 - 0.05 * player.perk_levels.get("Iron Will", 0)
                        if player.companion == "Cat":
                            cost_mult *= 0.9
                        player.energy = max(player.energy - 0.02 * cost_mult, 0)
                    player.rect = next_rect

        near_building = None
        for b in BUILDINGS:
            if player.rect.colliderect(b.rect):
                near_building = b
                break
        near_npc = None
        for n in NPCS:
            if player.rect.colliderect(n.rect):
                near_npc = n
                break
        if not inside_home and not inside_bar and not inside_forest:
            for b in BUILDINGS:
                if player.rect.colliderect(b.rect):
                    near_building = b
                    break

        if not inside_home and not inside_bar and not inside_forest and not in_building and shop_message_timer == 0 and not show_log:
            location = near_building.btype if near_building else None
            desc = random_event(player, location)
            if desc:
                shop_message = desc
                shop_message_timer = 90
                quest_sound.play()
                if SOUND_ENABLED:
                    quest_sound.play()

        if (
            not inside_home
            and not inside_bar
            and not inside_forest
            and not in_building
            and near_npc
            and not show_inventory
            and not show_log
        ):
            if keys[pygame.K_e]:
                state = player.npc_progress.get(near_npc.name)
                if state is None:
                    shop_message = f"{near_npc.name}: {near_npc.quest.description}"
                    player.side_quest = near_npc.quest.name
                    player.npc_progress[near_npc.name] = 1
                elif state == 1 and player.side_quest is None:
                    near_npc.quest.reward(player)
                    player.npc_progress[near_npc.name] = 2
                    shop_message = f"{near_npc.name}: Thanks for the help!"
                else:
                    shop_message = f"{near_npc.name}: Good to see you."
                shop_message_timer = 90

        if not inside_home and not inside_bar and not inside_forest and not in_building and near_building and not show_inventory and not show_log:
            if keys[pygame.K_e]:
                if building_open(near_building.btype, player.time, player):
                    in_building = near_building.btype

                    enter_sound.play()
                    if near_building.btype == "home":
                        inside_home = True
                        home_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            DOOR_RECT.x + 10,
                            DOOR_RECT.y + DOOR_RECT.height - PLAYER_SIZE - 10,
                        )
                    elif near_building.btype == "bar":
                        inside_bar = True
                        bar_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            BAR_DOOR_RECT.x + 10,
                            BAR_DOOR_RECT.y + BAR_DOOR_RECT.height - PLAYER_SIZE - 10,
                        )
                    elif near_building.btype == "forest":
                        inside_forest = True
                        forest_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            FOREST_DOOR_RECT.x + 10,
                            FOREST_DOOR_RECT.y + FOREST_DOOR_RECT.height - PLAYER_SIZE - 10,
                        )
                    else:
                        in_building = near_building.btype
                    if SOUND_ENABLED:
                        enter_sound.play()

                else:
                    shop_message = "Closed right now"
                    shop_message_timer = 60

        if in_building:
            if keys[pygame.K_q]:
                in_building = None

        if player.energy == 0:
            player.health = max(player.health - 0.08, 0)

        cam_x = min(max(0, player.rect.centerx - settings.SCREEN_WIDTH // 2), MAP_WIDTH - settings.SCREEN_WIDTH)
        cam_y = min(max(0, player.rect.centery - settings.SCREEN_HEIGHT // 2), MAP_HEIGHT - settings.SCREEN_HEIGHT)
        if inside_home:
            cam_x = cam_y = 0
            draw_home_interior(screen, font, player, frame if dx or dy else 0, BED_RECT, DOOR_RECT)
        elif inside_bar:
            cam_x = cam_y = 0
            draw_bar_interior(
                screen,
                font,
                player,
                frame if dx or dy else 0,
                COUNTER_RECT,
                BJ_RECT,
                SLOT_RECT,
                DART_RECT,
                BRAWL_RECT,
                BAR_DOOR_RECT,
            )
        elif inside_forest:
            cam_x = cam_y = 0
            draw_forest_area(
                screen,
                font,
                player,
                frame if dx or dy else 0,
                FOREST_ENEMY_RECTS,
                FOREST_DOOR_RECT,
            )
        else:
            cam_x = min(max(0, player.rect.centerx - settings.SCREEN_WIDTH // 2), MAP_WIDTH - settings.SCREEN_WIDTH)
            cam_y = min(max(0, player.rect.centery - settings.SCREEN_HEIGHT // 2), MAP_HEIGHT - settings.SCREEN_HEIGHT)

        draw_sky(screen)

        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)

        for b in BUILDINGS:
            draw_rect = b.rect.move(-cam_x, -cam_y)
            draw_building(screen, Building(draw_rect, b.name, b.btype))

        for n in NPCS:
            nr = n.rect.move(-cam_x, -cam_y)
            draw_npc(screen, nr)

        pr = player.rect.move(-cam_x, -cam_y)
        draw_player_sprite(screen, pr, frame if dx or dy else 0)

        draw_day_night(screen, player.time)


        draw_ui(screen, font, player, QUESTS, STORY_QUESTS)
        if show_inventory:
            draw_inventory_screen(
                screen,
                font,
                player,
                slot_rects,
                item_rects,
                (dragging_item, drag_pos) if dragging_item else None,
            )
        if show_perk_menu:
            draw_perk_menu(screen, font, player, PERKS)
        if show_log:
            draw_quest_log(screen, font, QUESTS, STORY_QUESTS)

        info_y = 46
        if near_npc and not in_building:
            msg = "[E] Talk"
            msg_surf = font.render(msg, True, (30, 30, 30))
            bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 6), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 210))
            screen.blit(bg, (10, info_y - 4))
            screen.blit(msg_surf, (18, info_y))
            info_y += 28

        if near_building and not in_building:
            msg = ""
            if near_building.btype == "job":
                pay = 30 + 20 * (player.office_level - 1)
                pay = 20 + 15 * (player.office_level - 1)
                msg = f"[E] to Work here (+${pay}, -20 energy)"
            elif near_building.btype == "dealer":
                pay = 50 + 25 * (player.dealer_level - 1)
                pay = 40 + 20 * (player.dealer_level - 1)
                msg = f"[E] to Deal drugs (+${pay}, -20 energy)"
            elif near_building.btype == "clinic":
                pay = 40 + 20 * (player.clinic_level - 1)
                pay = 30 + 15 * (player.clinic_level - 1)
                msg = f"[E] to Work here (+${pay}, -20 energy)"
            elif near_building.btype == "home":
                msg = "[E] to Sleep (restore energy, next day)"
                msg = "[E] to enter home"
            elif near_building.btype == "shop":
                msg = "[E] to shop for items"
            elif near_building.btype == "gym":
                msg = "[E] to train (+1 STR, +5 health, -10 energy, -$10)"
            elif near_building.btype == "library":
                msg = "[E] to study (+1 INT, -5 energy, -$5)"
                msg += "  [P] puzzle"
            elif near_building.btype == "park":
                msg = "[E] to chat (+1 CHA, -5 energy)  [F] fish"
            elif near_building.btype == "bar":
                msg = "[E] to gamble and fight"
                msg += "  [D] darts"
            elif near_building.btype == "dungeon":
                msg = "[E] to fight an enemy"
            elif near_building.btype == "forest":
                msg = "[E] to explore the woods"
            elif near_building.btype == "petshop":
                msg = "[E] to adopt a pet"
            elif near_building.btype == "bank":
                msg = "[E] to visit the bank"
            elif near_building.btype == "townhall":
                msg = "[E] to visit the Town Hall"
            elif near_building.btype == "workshop":
                msg = "[E] to craft gear"
            elif near_building.btype == "farm":
                msg = "[E] to manage crops"
            elif near_building.btype == "mall":
                msg = "[E] to browse the mall"
            elif near_building.btype == "beach":
                msg = "[E] to relax at the beach"
            elif near_building.btype == "suburbs":
                msg = "[E] to visit the suburbs"
            if msg:
                if not building_open(near_building.btype, player.time, player):
                    msg += " (Closed)"
                msg_surf = font.render(msg, True, (30, 30, 30))
                bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 6), pygame.SRCALPHA)
                bg.fill((255, 255, 255, 210))
                screen.blit(bg, (10, info_y - 4))
                screen.blit(msg_surf, (18, info_y))

        if in_building:
            panel = pygame.Surface((settings.SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, settings.SCREEN_HEIGHT - 100))
            txt = ""
            if in_building == "job":
                pay = 30 + 20 * (player.office_level - 1)
                pay = 20 + 15 * (player.office_level - 1)
                txt = f"[E] Work (+${pay})  [Q] Leave"
            elif in_building == "dealer":
                pay = 50 + 25 * (player.dealer_level - 1)
                pay = 40 + 20 * (player.dealer_level - 1)
                txt = f"[E] Deal (+${pay})  [Q] Leave"
            elif in_building == "clinic":
                pay = 40 + 20 * (player.clinic_level - 1)
                pay = 30 + 15 * (player.clinic_level - 1)
                txt = f"[E] Work (+${pay})  [Q] Leave"
            elif in_building == "home":
                txt = "[E] Sleep  [1-9] Buy upgrade  [Q] Leave"
            elif in_building == "shop":
                txt = "[0-9] Buy items  [Q] Leave"
            elif in_building == "gym":
                txt = "[E] Train  [Q] Leave"
            elif in_building == "library":
                txt = "[E] Study  [P] Puzzle  [Q] Leave"
            elif in_building == "park":
                txt = "[E] Chat  [F] Fish  [Q] Leave"
            elif in_building == "bank":
                txt = f"[E] Talk  [D] Deposit $10  [W] Withdraw $10  [Q] Leave  Bal:${int(player.bank_balance)}"
            elif in_building == "bar":
                txt = "[B] Buy token  [J] Blackjack  [S] Slots  [D] Darts  [F] Fight  [Q] Leave"
            elif in_building == "dungeon":
                txt = "[E] Fight  [Q] Leave"
            elif in_building == "forest":
                txt = "[E] Fight  [Q] Leave"
            elif in_building == "petshop":
                txt = "[1-3] Adopt  [Q] Leave"
            elif in_building == "workshop":
                txt = "1 Potion 2 Sword 3 Up Wpn 4 Up Arm  [Q] Leave"
            elif in_building == "farm":
                txt = "[P] Plant seed  [H] Harvest  [Q] Leave"
            elif in_building == "mall":
                txt = "[E] Pick up order  [Q] Leave"
            elif in_building == "beach":
                txt = "[E] Relax/Deliver  [Q] Leave"
            elif in_building == "suburbs":
                txt = "[E] Help locals  [Q] Leave"
            tip_surf = font.render(f"Inside: {in_building.upper()}   {txt}", True, (80, 40, 40))
            screen.blit(tip_surf, (20, settings.SCREEN_HEIGHT - 80))
            if in_building == "shop":
                for i, (name, cost, _func) in enumerate(SHOP_ITEMS):
                    item_surf = font.render(f"{(i+1)%10}:{name} ${cost}", True, (80, 40, 40))
                    row = i // 5
                    col = i % 5
                    screen.blit(item_surf, (30 + col * 150, settings.SCREEN_HEIGHT - 60 - row * 24))
                    screen.blit(item_surf, (30 + col * 200, settings.SCREEN_HEIGHT - 60 - row * 24))
            elif in_building == "home":
                avail = [u for u in HOME_UPGRADES if u[3] <= player.home_level]
                for i, (name, cost, _d, _req) in enumerate(avail):
                    status = "Owned" if name in player.home_upgrades else f"${cost}"
                    item_surf = font.render(f"{i+1}:{name} {status}", True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 260, settings.SCREEN_HEIGHT - 60))
            elif in_building == "petshop":
                for i, (name, cost, _d) in enumerate(COMPANIONS):
                    item_surf = font.render(f"{i+1}:{name} ${cost}", True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 200, settings.SCREEN_HEIGHT - 60))
            elif in_building == "workshop":
                opts = [
                    "1:Health Potion (2 herbs)",
                    "2:Iron Sword (3 metal)",
                    "3:Upgrade Weapon (2 metal)",
                    "4:Upgrade Armor (2 cloth)",
                ]
                for i, txt_opt in enumerate(opts):
                    item_surf = font.render(txt_opt, True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 300, settings.SCREEN_HEIGHT - 60))
            elif in_building == "farm":
                opts = ["P:Plant (-1 seed)", "H:Harvest (ready crops)"]
                for i, txt_opt in enumerate(opts):
                    item_surf = font.render(txt_opt, True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 260, settings.SCREEN_HEIGHT - 60))

        elif inside_bar:
            panel = pygame.Surface((settings.SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, settings.SCREEN_HEIGHT - 100))
            txt = "Use counter to buy tokens, tables to gamble or throw darts, ring to fight, door to exit"
            tip_surf = font.render(txt, True, (80, 40, 40))
            screen.blit(tip_surf, (20, settings.SCREEN_HEIGHT - 80))
        elif inside_forest:
            panel = pygame.Surface((settings.SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, settings.SCREEN_HEIGHT - 100))
            txt = "Fight enemies or exit via the door"
            tip_surf = font.render(txt, True, (80, 40, 40))
            screen.blit(tip_surf, (20, settings.SCREEN_HEIGHT - 80))
        elif inside_home:
            panel = pygame.Surface((settings.SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, settings.SCREEN_HEIGHT - 100))
            txt = "Use bed to sleep, door to exit" \
                " 1-3 Buy upgrade"
            tip_surf = font.render(txt, True, (80, 40, 40))
            screen.blit(tip_surf, (20, settings.SCREEN_HEIGHT - 80))

        if shop_message_timer > 0:
            shop_message_timer -= 1
            msg_surf = font.render(shop_message, True, (220, 40, 40))
            bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 240))
            screen.blit(bg, (10, 90))
            screen.blit(msg_surf, (18, 94))

        if player.health <= 0:
            over = font.render("GAME OVER (You collapsed from exhaustion)", True, (255, 0, 0))
            screen.blit(over, (settings.SCREEN_WIDTH // 2 - 240, settings.SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        if check_quests(player):
            quest_sound.play()
            if SOUND_ENABLED:
                quest_sound.play()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()