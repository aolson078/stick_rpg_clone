import sys
import os
import json
import random
import pygame

from entities import Player, Building, Quest, Event, InventoryItem
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
)
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
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

pygame.init()
pygame.mixer.init()

BUILDINGS = [
    Building(pygame.Rect(200, 150, 200, 120), "Home", "home"),
    Building(pygame.Rect(600, 300, 180, 240), "Office", "job"),
    Building(pygame.Rect(1100, 700, 300, 100), "Shop", "shop"),
    Building(pygame.Rect(400, 900, 160, 180), "Park", "park"),
    Building(pygame.Rect(460, 960, 80, 80), "Deal Spot", "dealer"),
    Building(pygame.Rect(900, 450, 220, 160), "Gym", "gym"),
    Building(pygame.Rect(1200, 250, 200, 160), "Library", "library"),
    Building(pygame.Rect(300, 600, 180, 160), "Clinic", "clinic"),
    Building(pygame.Rect(800, 750, 200, 150), "Bar", "bar"),
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
}


# Simple quests that encourage visiting different locations
QUESTS = [
    Quest("Earn $200", lambda p: p.money >= 200),
    Quest("Reach STR 5", lambda p: p.strength >= 5),
    Quest("Reach INT 5", lambda p: p.intelligence >= 5),
]


# Random events that may occur while exploring
def _ev_found_money(p: Player) -> None:
    bonus = 5 * p.perk_levels.get("Lucky", 0)
    p.money += 5 + bonus


def _ev_gain_int(p: Player) -> None:
    p.intelligence += 1 + p.perk_levels.get("Lucky", 0)


def _ev_gain_cha(p: Player) -> None:
    p.charisma += 1 + p.perk_levels.get("Lucky", 0)


def _ev_trip(p: Player) -> None:
    p.health = max(p.health - 5, 0)


def _ev_theft(p: Player) -> None:
    p.money = max(p.money - 10, 0)


EVENTS = [
    Event("You found $5 on the ground!", _ev_found_money),
    Event("Someone shared a study tip. +1 INT", _ev_gain_int),
    Event("You chatted with locals. +1 CHA", _ev_gain_cha),
    Event("You tripped and hurt yourself. -5 health", _ev_trip),
    Event("A thief stole $10 from you!", _ev_theft),
]

# Items sold at the shop: name, cost, and effect function
SHOP_ITEMS = [
    ("Cola", 3, lambda p: setattr(p, "energy", min(100, p.energy + 5))),
    ("Protein Bar", 7, lambda p: setattr(p, "health", min(100, p.health + 5))),
    ("Book", 10, lambda p: setattr(p, "intelligence", p.intelligence + 1)),
    ("Gym Pass", 15, lambda p: setattr(p, "strength", p.strength + 1)),
    ("Charm Pendant", 20, lambda p: setattr(p, "charisma", p.charisma + 1)),
    ("Skateboard", 40, lambda p: setattr(p, "has_skateboard", True)),
    (
        "Leather Helmet",
        25,
        lambda p: p.inventory.append(
            InventoryItem("Leather Helmet", "head", defense=1)
        ),
    ),
    (
        "Leather Armor",
        40,
        lambda p: p.inventory.append(
            InventoryItem("Leather Armor", "chest", defense=2)
        ),
    ),
    (
        "Leather Boots",
        20,
        lambda p: p.inventory.append(
            InventoryItem("Leather Boots", "legs", defense=1, speed=1)
        ),
    ),
    (
        "Wooden Sword",
        35,
        lambda p: p.inventory.append(
            InventoryItem("Wooden Sword", "weapon", attack=2)
        ),
    ),
]

# Upgrades available for purchase inside the home
HOME_UPGRADES = [
    ("Comfy Bed", 50, "Recover +20 energy when sleeping"),
    ("Decorations", 40, "Gain +1 CHA each morning"),
    ("Study Desk", 60, "Gain +1 INT each morning"),
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


def buy_home_upgrade(player: Player, index: int) -> str:
    """Attempt to purchase a home upgrade by index."""
    if index < 0 or index >= len(HOME_UPGRADES):
        return "Invalid upgrade"
    name, cost, _ = HOME_UPGRADES[index]
    if name in player.home_upgrades:
        return "Already owned"
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    player.home_upgrades.append(name)
    return f"Bought {name}"

EVENT_CHANCE = 0.0008  # roughly once every ~20s at 60 FPS

SAVE_FILE = "savegame.json"



def building_open(btype, minutes):
    start, end = OPEN_HOURS.get(btype, (0, 24))
    hour = (minutes / 60) % 24
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end



def check_quests(player):
    new = False
    for q in QUESTS:
        if not q.completed and q.check(player):
            q.completed = True
            new = True
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


def random_event(player: Player) -> str | None:
    """Possibly trigger a random event and return its description."""
    if random.random() < EVENT_CHANCE:
        ev = random.choice(EVENTS)
        ev.apply(player)
        return ev.description
    return None


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


def _combat_stats(player: Player):
    atk = player.strength
    df = player.defense
    spd = player.speed
    if player.perk_levels.get("Bar Champion"):
        atk += 2
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
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            dmg = max(1, p_atk - enemy["defense"])
            e_hp -= dmg
        else:
            dmg = max(1, enemy["attack"] - p_def)
            p_hp -= dmg
        turn_player = not turn_player
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

        "has_skateboard": player.has_skateboard,
        "home_upgrades": player.home_upgrades,
        "perk_points": player.perk_points,
        "perk_levels": player.perk_levels,
        "next_strength_perk": player.next_strength_perk,
        "next_intelligence_perk": player.next_intelligence_perk,
        "next_charisma_perk": player.next_charisma_perk,
        "inventory": [item.__dict__ for item in player.inventory],
        "equipment": {
            slot: (it.__dict__ if it else None) for slot, it in player.equipment.items()
        },

        "x": player.rect.x,
        "y": player.rect.y,
        "quests": [q.completed for q in QUESTS],
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

    player.has_skateboard = data.get("has_skateboard", player.has_skateboard)
    player.home_upgrades = data.get("home_upgrades", [])
    player.perk_points = data.get("perk_points", 0)
    player.perk_levels = data.get("perk_levels", {})
    player.next_strength_perk = data.get("next_strength_perk", 5)
    player.next_intelligence_perk = data.get("next_intelligence_perk", 5)
    player.next_charisma_perk = data.get("next_charisma_perk", 5)
    for item in data.get("inventory", []):
        player.inventory.append(InventoryItem(**item))
    for slot, item in data.get("equipment", {}).items():
        if item:
            player.equipment[slot] = InventoryItem(**item)

    for completed, q in zip(data.get("quests", []), QUESTS):
        q.completed = completed
    return player


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
    enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
    quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
    for snd in (step_sound, enter_sound, quest_sound):
        snd.set_volume(SFX_VOLUME)
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(-1)

    load_player_sprites()

    player = Player(pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE))
    loaded_player = load_game()
    shop_message = ""
    if loaded_player:
        player = loaded_player
        shop_message = "Game loaded!"
        shop_message_timer = 60
    else:
        shop_message_timer = 0
    in_building = None
    frame = 0
    show_inventory = False
    show_perk_menu = False
    dragging_item = None
    drag_origin = None
    drag_pos = (0, 0)
    slot_rects = {
        "head": pygame.Rect(150, 150, 100, 60),
        "chest": pygame.Rect(150, 220, 100, 60),
        "arms": pygame.Rect(150, 290, 100, 60),
        "legs": pygame.Rect(150, 360, 100, 60),
        "weapon": pygame.Rect(150, 430, 100, 60),
    }

    while True:
        frame += 1
        player.time += MINUTES_PER_FRAME
        if player.time >= 1440:
            player.time -= 1440
            player.day += 1
        if check_perk_unlocks(player):
            shop_message = "Gained a perk point! Press P to spend"
            shop_message_timer = 90
        secret = check_hidden_perks(player)
        if secret:
            shop_message = secret
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
            if event.type == pygame.KEYDOWN and in_building:
                if in_building == "job":
                    if player.energy >= 20:
                        pay = 30 + 20 * (player.office_level - 1)
                        player.money += pay
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
                    if event.key == pygame.K_e:
                        player.energy = 100
                        if "Comfy Bed" in player.home_upgrades:
                            player.energy += 20
                        player.energy += 10 * player.perk_levels.get("Night Owl", 0)
                        player.time = 8 * 60
                        player.day += 1
                        if "Decorations" in player.home_upgrades:
                            player.charisma += 1
                        if "Study Desk" in player.home_upgrades:
                            player.intelligence += 1
                        if player.perk_levels.get("Home Owner"):
                            player.health = min(player.health + 10, 100)
                        shop_message = "You slept. New day!"
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
                elif in_building == "gym":
                    if player.money >= 10 and player.energy >= 10:
                        player.money -= 10
                        player.energy -= energy_cost(player, 10)
                        player.health = min(player.health + 5, 100)
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
                elif in_building == "library":
                    if player.money >= 5 and player.energy >= 5:
                        player.money -= 5
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Book Worm", 0)
                        gain = 1 + bonus
                        player.intelligence += gain
                        msg_gain = f" +{gain} INT"
                        shop_message = "You studied!" + msg_gain
                    elif player.money < 5:
                        shop_message = "Need $5 to study"
                    else:
                        shop_message = "Too tired to study!"
                    shop_message_timer = 60
                elif in_building == "park":
                    if player.energy >= 5:
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Social Butterfly", 0)
                        gain = 1 + bonus
                        player.charisma += gain
                        msg_gain = f" +{gain} CHA"
                        shop_message = "You socialized!" + msg_gain
                    else:
                        shop_message = "Too tired to chat!"
                    shop_message_timer = 60
                elif in_building == "bar":
                    if event.key == pygame.K_b:
                        if player.money >= 10:
                            player.money -= 10
                            player.tokens += 1
                            shop_message = "Bought a token"
                        else:
                            shop_message = "Need $10" 
                    elif event.key == pygame.K_j:
                        shop_message = play_blackjack(player)
                    elif event.key == pygame.K_s:
                        shop_message = play_slots(player)
                    elif event.key == pygame.K_f:
                        shop_message = fight_brawler(player)
                    elif event.key == pygame.K_e:
                        shop_message = "Buy tokens with B"  # hint when pressing E
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "dealer":
                    if player.energy >= 20:
                        pay = 50 + 25 * (player.dealer_level - 1)
                        player.money += pay
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
                elif in_building == "clinic":
                    if player.energy >= 20:
                        pay = 40 + 20 * (player.clinic_level - 1)
                        player.money += pay
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
        if not in_building and not show_inventory:
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
                        if frame % 12 == 0:
                            step_sound.play()
                        player.energy = max(player.energy - 0.04 * (1 - 0.05 * player.perk_levels.get("Iron Will", 0)), 0)
                    player.rect = next_rect

        near_building = None
        for b in BUILDINGS:
            if player.rect.colliderect(b.rect):
                near_building = b
                break

        if not in_building and shop_message_timer == 0:
            desc = random_event(player)
            if desc:
                shop_message = desc
                shop_message_timer = 90
                quest_sound.play()

        if not in_building and near_building and not show_inventory:
            if keys[pygame.K_e]:
                if building_open(near_building.btype, player.time):
                    in_building = near_building.btype

                    enter_sound.play()

                else:
                    shop_message = "Closed right now"
                    shop_message_timer = 60

        if in_building:
            if keys[pygame.K_q]:
                in_building = None

        if player.energy == 0:
            player.health = max(player.health - 0.08, 0)

        cam_x = min(max(0, player.rect.centerx - SCREEN_WIDTH // 2), MAP_WIDTH - SCREEN_WIDTH)
        cam_y = min(max(0, player.rect.centery - SCREEN_HEIGHT // 2), MAP_HEIGHT - SCREEN_HEIGHT)

        screen.fill(BG_COLOR)

        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)

        for b in BUILDINGS:
            draw_rect = b.rect.move(-cam_x, -cam_y)
            draw_building(screen, Building(draw_rect, b.name, b.btype))

        pr = player.rect.move(-cam_x, -cam_y)
        draw_player_sprite(screen, pr, frame if dx or dy else 0)

        draw_day_night(screen, player.time)


        draw_ui(screen, font, player, QUESTS)
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

        info_y = 46
        if near_building and not in_building:
            msg = ""
            if near_building.btype == "job":
                pay = 30 + 20 * (player.office_level - 1)
                msg = f"[E] to Work here (+${pay}, -20 energy)"
            elif near_building.btype == "dealer":
                pay = 50 + 25 * (player.dealer_level - 1)
                msg = f"[E] to Deal drugs (+${pay}, -20 energy)"
            elif near_building.btype == "clinic":
                pay = 40 + 20 * (player.clinic_level - 1)
                msg = f"[E] to Work here (+${pay}, -20 energy)"
            elif near_building.btype == "home":
                msg = "[E] to enter home"
            elif near_building.btype == "shop":
                msg = "[E] to shop for items"
            elif near_building.btype == "gym":
                msg = "[E] to train (+1 STR, +5 health, -10 energy, -$10)"
            elif near_building.btype == "library":
                msg = "[E] to study (+1 INT, -5 energy, -$5)"
            elif near_building.btype == "park":
                msg = "[E] to chat (+1 CHA, -5 energy)"
            elif near_building.btype == "bar":
                msg = "[E] to gamble and fight"
            if msg:
                if not building_open(near_building.btype, player.time):
                    msg += " (Closed)"
                msg_surf = font.render(msg, True, (30, 30, 30))
                bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 6), pygame.SRCALPHA)
                bg.fill((255, 255, 255, 210))
                screen.blit(bg, (10, info_y - 4))
                screen.blit(msg_surf, (18, info_y))

        if in_building:
            panel = pygame.Surface((SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, SCREEN_HEIGHT - 100))
            txt = ""
            if in_building == "job":
                pay = 30 + 20 * (player.office_level - 1)
                txt = f"[E] Work (+${pay})  [Q] Leave"
            elif in_building == "dealer":
                pay = 50 + 25 * (player.dealer_level - 1)
                txt = f"[E] Deal (+${pay})  [Q] Leave"
            elif in_building == "clinic":
                pay = 40 + 20 * (player.clinic_level - 1)
                txt = f"[E] Work (+${pay})  [Q] Leave"
            elif in_building == "home":
                txt = "[E] Sleep  [1-3] Buy upgrade  [Q] Leave"
            elif in_building == "shop":
                txt = "[0-9] Buy items  [Q] Leave"
            elif in_building == "gym":
                txt = "[E] Train  [Q] Leave"
            elif in_building == "library":
                txt = "[E] Study  [Q] Leave"
            elif in_building == "park":
                txt = "[E] Chat  [Q] Leave"
            elif in_building == "bar":
                txt = "[B] Buy token  [J] Blackjack  [S] Slots  [F] Fight  [Q] Leave"
            tip_surf = font.render(f"Inside: {in_building.upper()}   {txt}", True, (80, 40, 40))
            screen.blit(tip_surf, (20, SCREEN_HEIGHT - 80))
            if in_building == "shop":
                for i, (name, cost, _func) in enumerate(SHOP_ITEMS):
                    item_surf = font.render(f"{(i+1)%10}:{name} ${cost}", True, (80, 40, 40))
                    row = i // 5
                    col = i % 5
                    screen.blit(item_surf, (30 + col * 150, SCREEN_HEIGHT - 60 - row * 24))
            elif in_building == "home":
                for i, (name, cost, _d) in enumerate(HOME_UPGRADES):
                    status = "Owned" if name in player.home_upgrades else f"${cost}"
                    item_surf = font.render(f"{i+1}:{name} {status}", True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 200, SCREEN_HEIGHT - 60))

        if shop_message_timer > 0:
            shop_message_timer -= 1
            msg_surf = font.render(shop_message, True, (220, 40, 40))
            bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 240))
            screen.blit(bg, (10, 90))
            screen.blit(msg_surf, (18, 94))

        if player.health <= 0:
            over = font.render("GAME OVER (You collapsed from exhaustion)", True, (255, 0, 0))
            screen.blit(over, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        if check_quests(player):
            quest_sound.play()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
