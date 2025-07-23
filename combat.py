"""Combat-related helper functions and constants."""
import random
from typing import List, Tuple
from entities import Player, InventoryItem

# Number of bar challengers
BRAWLER_COUNT = 5

# Three enemies found in the forest
FOREST_ENEMIES: List[dict] = [
    {"attack": 4, "defense": 1, "speed": 2, "health": 20, "reward": 30},
    {"attack": 6, "defense": 2, "speed": 3, "health": 28, "reward": 45},
    {"attack": 8, "defense": 3, "speed": 2, "health": 36, "reward": 60},
]

# Stats for the ultimate boss encountered at the end of the game
FINAL_BOSS = {
    "attack": 12,
    "defense": 6,
    "speed": 4,
    "health": 80,
    "reward": 200,
}

# Combat tweaks
DODGE_BASE = 0.1
POWER_STRIKE_CHANCE = 0.25
BLEED_TURNS = 3
BLEED_DAMAGE = 1


def energy_cost(player: Player, base: float) -> float:
    """Return energy cost adjusted by Iron Will and secret perks."""
    level = player.perk_levels.get("Iron Will", 0)
    cost = base * (1 - 0.05 * level)
    if player.perk_levels.get("Perk Master"):
        cost *= 0.9
    return cost


def _combat_stats(player: Player) -> Tuple[int, int, int, int]:
    """Return player's attack, defense, speed and combo with equipment."""
    weapon = player.equipment.get("weapon")
    base_atk = player.strength
    if weapon:
        wtype = getattr(weapon, "weapon_type", "melee")
        if wtype == "ranged":
            base_atk = player.speed
        elif wtype == "magic":
            base_atk = player.intelligence

    atk = base_atk
    df = player.defense
    spd = player.speed
    combo = 1
    if player.perk_levels.get("Bar Champion"):
        atk += 2
    if player.companion == "Dog":
        df += 1
    elif player.companion == "Rhino":
        atk += 1
    for item in player.equipment.values():
        if item:
            atk += item.attack
            df += item.defense
            spd += item.speed
            if item.slot == "weapon":
                combo = getattr(item, "combo", 1)
    return atk, df, spd, combo


def fight_brawler(player: Player) -> str:
    """Challenge a random bar brawler and return the fight result."""
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
    p_atk, p_def, p_spd, p_combo = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            for _ in range(p_combo):
                dmg = max(1, p_atk - enemy["defense"])
                if (
                    not special_used and random.random() < POWER_STRIKE_CHANCE
                ):
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
    reward = 20 + stage * 10
    player.money += reward
    player.brawls_won += 1
    msg = f"You won the fight {stage}! +${reward}"
    if player.brawls_won == BRAWLER_COUNT:
        msg += " All brawlers defeated!"
    return msg


def fight_enemy(player: Player) -> str:
    """Fight a random street enemy and return a message."""
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
    p_atk, p_def, p_spd, p_combo = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            for _ in range(p_combo):
                dmg = max(1, p_atk - enemy["defense"])
                if (
                    not special_used and random.random() < POWER_STRIKE_CHANCE
                ):
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
    if player.companion == "Parrot":
        chance = 0.3 + 0.2 * (player.companion_level - 1)
        if random.random() < chance:
            player.tokens += 1
            loot += " (parrot found another)"
    player.enemies_defeated += 1
    return f"Enemy defeated! +${cash}{loot}"


def fight_forest_enemy(player: Player, index: int) -> str:
    """Fight one of the fixed forest enemies by list index."""
    if index < 0 or index >= len(FOREST_ENEMIES):
        return "Invalid enemy"
    if player.energy < 10:
        return "Too tired to fight!"
    player.energy -= energy_cost(player, 10)

    enemy = FOREST_ENEMIES[index]
    p_atk, p_def, p_spd, p_combo = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            for _ in range(p_combo):
                dmg = max(1, p_atk - enemy["defense"])
                if (
                    not special_used and random.random() < POWER_STRIKE_CHANCE
                ):
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


def fight_final_boss(player: Player) -> str:
    """Battle the ultimate boss. Returns the fight result message."""
    if player.boss_defeated:
        return "The boss has already been slain"
    if player.energy < 20:
        return "Too tired to fight!"
    player.energy -= energy_cost(player, 20)

    enemy = FINAL_BOSS
    p_atk, p_def, p_spd, p_combo = _combat_stats(player)
    p_hp = player.health
    e_hp = enemy["health"]
    turn_player = p_spd >= enemy["speed"]
    special_used = False
    bleed_turns = 0
    while p_hp > 0 and e_hp > 0:
        if turn_player:
            for _ in range(p_combo):
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
        return "You were defeated by the boss!"

    player.money += enemy["reward"]
    player.boss_defeated = True
    # Legendary sword reward
    player.inventory.append(InventoryItem("Legendary Sword", "weapon", attack=8, speed=1, combo=2))
    return "Boss defeated! You earned the Legendary Sword"
