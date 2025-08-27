"""Item and inventory handling extracted from game.py."""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from entities import Player, InventoryItem
from combat import energy_cost
import factions
from constants import PERK_MAX_LEVEL
import random

# Items sold at the shop: name, cost, and effect
SHOP_ITEMS: List[Tuple[str, int, any]] = [
    ("Cola", 3, lambda p: p.inventory.append(InventoryItem("Cola", "consumable"))),
    (
        "Protein Bar",
        7,
        lambda p: p.inventory.append(InventoryItem("Protein Bar", "consumable")),
    ),
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
            InventoryItem("Wooden Sword", "weapon", attack=2, combo=1)
        ),
    ),
    (
        "Spear",
        55,
        lambda p: p.inventory.append(
            InventoryItem("Spear", "weapon", attack=3, combo=2)
        ),
    ),
    (
        "Bow",
        70,
        lambda p: p.inventory.append(
            InventoryItem(
                "Bow", "weapon", attack=2, speed=1, combo=2, weapon_type="ranged"
            )
        ),
    ),
    (
        "Magic Wand",
        80,
        lambda p: p.inventory.append(
            InventoryItem(
                "Magic Wand", "weapon", attack=3, speed=1, combo=1, weapon_type="magic"
            )
        ),
    ),
    (
        "Crossbow",
        90,
        lambda p: p.inventory.append(
            InventoryItem("Crossbow", "weapon", attack=4, combo=2, weapon_type="ranged")
        ),
    ),
]

# Loaded crop data
CROPS_PATH = Path(__file__).parent / "data" / "crops.json"
if CROPS_PATH.exists():
    with open(CROPS_PATH) as f:
        _crops = json.load(f)
    CROPS: Dict[str, Dict] = {c["name"]: c for c in _crops}
else:
    CROPS = {}

# Add seed options for each crop
for _name, _data in CROPS.items():
    cost = _data.get("sell_price", 10)
    SHOP_ITEMS.append(
        (
            f"{_name} Seeds x3",
            cost,
            lambda p, n=_name: p.resources.__setitem__(
                f"{n}_seeds", p.resources.get(f"{n}_seeds", 0) + 3
            ),
        )
    )

# Loaded crafting recipes
RECIPES_PATH = Path(__file__).parent / "data" / "recipes.json"
if RECIPES_PATH.exists():
    with open(RECIPES_PATH) as f:
        _recipes = json.load(f)
    RECIPES: Dict[str, Dict] = {r["name"]: r for r in _recipes}
else:
    RECIPES = {}

# Seasonal price modifiers applied to shop items
SEASON_PRICE_MODIFIERS = {
    "Spring": 1.0,
    "Summer": 0.9,
    "Fall": 1.1,
    "Winter": 1.2,
}


def _daily_price_multiplier(day: int) -> float:
    """Return a deterministic daily multiplier based on the day number."""
    if day == 1:
        return 1.0
    rnd = random.Random(day).random()
    return 0.8 + rnd * 0.4  # range 0.8 - 1.2


def get_shop_price(player: Player, index: int) -> int:
    """Return the current price for a shop item considering season and day."""
    base_cost = SHOP_ITEMS[index][1]
    season_mult = SEASON_PRICE_MODIFIERS.get(player.season, 1.0)
    day_mult = _daily_price_multiplier(player.day)
    cost = int(round(base_cost * season_mult * day_mult))
    discount = factions.get_business_discount(player)
    return int(round(cost * discount))

# Upgrades available for purchase inside the home
HOME_UPGRADES: List[Tuple[str, int, str, int]] = [
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
    ("Llama", 130, "SPD +1, crops sell for more"),
    ("Peacock", 160, "CHA +1, extra CHA from chatting"),
    ("Rhino", 200, "STR +1, boosts attack"),
]

# Ability trees for each companion
COMPANION_ABILITIES: Dict[str, List[Tuple[str, str, str]]] = {
    "Dog": [
        ("Fetch", "Chance to bring money when sleeping", "money"),
        ("Guard", "+1 DEF per level", "defense"),
        ("Bite", "+1 STR per level", "strength"),
    ],
    "Cat": [
        ("Sneak", "Reduced travel energy cost", "speed"),
        ("Inspire", "+1 CHA per level", "charisma"),
        ("Pounce", "+1 STR per level", "strength"),
    ],
    "Parrot": [
        ("Mimic", "+1 INT per level", "intelligence"),
        ("Scout", "Chance for extra tokens", "tokens"),
        ("Squawk", "Small enemy stun chance", "strength"),
    ],
    "Llama": [
        ("Sprint", "+1 SPD per level", "speed"),
        ("Graze", "Crops sell for more", "money"),
        ("Kick", "+1 STR per level", "strength"),
    ],
    "Peacock": [
        ("Strut", "Extra CHA from chatting", "charisma"),
        ("Dazzle", "Chance to charm enemies", "charisma"),
        ("Display", "+1 CHA per level", "charisma"),
    ],
    "Rhino": [
        ("Charge", "+1 STR per level", "strength"),
        ("Thick Hide", "+1 DEF per level", "defense"),
        ("Trample", "Boost attack damage", "strength"),
    ],
}


def buy_shop_item(player: Player, index: int) -> str:
    """Purchase an item from the shop list by index."""
    if index < 0 or index >= len(SHOP_ITEMS):
        return "Invalid item"
    name, _base_cost, effect = SHOP_ITEMS[index]
    if name == "Skateboard" and player.has_skateboard:
        return "Already have skateboard"
    cost = get_shop_price(player, index)
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    effect(player)
    return f"Bought {name}"


def buy_home_upgrade(player: Player, index: int) -> str:
    """Buy a house upgrade if unlocked and affordable."""
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
    """Return upgrades unlocked for the player's current home level."""
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
    """Adopt a pet companion if you can afford it."""
    if index < 0 or index >= len(COMPANIONS):
        return "Invalid choice"
    name, cost, _desc = COMPANIONS[index]
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    player.companion = name
    player.companion_level = 1
    player.companion_morale = 100
    player.companion_abilities[name] = {
        abil[0]: 0 for abil in COMPANION_ABILITIES.get(name, [])
    }
    if name == "Dog":
        player.defense += 1
    elif name == "Cat":
        player.charisma += 1
    elif name == "Parrot":
        player.intelligence += 1
    elif name == "Llama":
        player.speed += 1
    elif name == "Peacock":
        player.charisma += 1
    elif name == "Rhino":
        player.strength += 1
    return f"Adopted {name}!"


def sort_inventory(player: Player, key: str) -> None:
    """Sort ``player.inventory`` in-place.

    ``key`` can be ``"name"``, ``"type"``, or ``"stat"``.  Name sorts
    alphabetically, type sorts by equipment slot then name, and stat sorts by
    the combined attack/defense/speed values in descending order.
    """

    if key == "name":
        player.inventory.sort(key=lambda i: i.name.lower())
    elif key == "type":
        player.inventory.sort(key=lambda i: (i.slot, i.name.lower()))
    elif key == "stat":
        player.inventory.sort(
            key=lambda i: i.attack + i.defense + i.speed,
            reverse=True,
        )



def plant_seed(player: Player, crop_type: Optional[str] = None) -> str:
    """Plant a seed of the given crop type if available."""
    # Determine crop if not specified: pick first seed available
    if crop_type is None:
        for name in CROPS:
            if player.resources.get(f"{name}_seeds", 0) > 0:
                crop_type = name
                break
        if crop_type is None:
            return "No seeds"
    if crop_type not in CROPS:
        return "Unknown crop"
    seed_key = f"{crop_type}_seeds"
    if player.resources.get(seed_key, 0) <= 0:
        return f"No {crop_type} seeds"
    player.resources[seed_key] -= 1
    player.crops.append({"type": crop_type, "planted_day": player.day})
    return f"Planted {crop_type}"


def harvest_crops(player: Player, crop_type: Optional[str] = None) -> str:
    """Harvest crops that have finished growing."""
    harvested = 0
    for crop in list(player.crops):
        if crop_type and crop["type"] != crop_type:
            continue
        data = CROPS.get(crop["type"])
        if not data:
            continue
        if player.day - crop["planted_day"] >= data.get("growth_days", 0):
            player.crops.remove(crop)
            key = crop["type"]
            player.resources[key] = player.resources.get(key, 0) + 1
            player.resources["produce"] = player.resources.get("produce", 0) + 1
            harvested += 1
    if harvested == 0:
        return "Nothing ready"
    return f"Harvested {harvested} produce"


def sell_produce(player: Player) -> str:
    """Sell all harvested produce for cash using crop-specific prices."""
    total_gain = 0
    sold_any = False
    bonus = 5 * player.companion_level if player.companion == "Llama" else 0
    for name, data in CROPS.items():
        count = player.resources.get(name, 0)
        if count > 0:
            price = data.get("sell_price", 0) + bonus
            total_gain += price * count
            player.resources[name] = 0
            sold_any = True
    if not sold_any:
        return "No produce"
    player.money += total_gain
    return f"Sold produce for ${total_gain}"


def buy_animal(player: Player, animal: str) -> str:
    """Purchase a farm animal if affordable."""
    costs = {"chicken": 20, "cow": 100}
    if animal not in costs:
        return "Invalid animal"
    cost = costs[animal]
    if player.money < cost:
        return f"Need ${cost}"
    player.money -= cost
    player.animals[animal] = player.animals.get(animal, 0) + 1
    return f"Bought a {animal}"


def feed_animals(player: Player, animal: str) -> str:
    """Feed animals of the given type to collect their products."""
    count = player.animals.get(animal, 0)
    if count <= 0:
        return f"No {animal}s"
    feed_costs = {"chicken": 1, "cow": 3}
    cost = feed_costs[animal] * count
    if player.money < cost:
        return f"Need ${cost}"
    player.money -= cost
    products = {"chicken": "eggs", "cow": "milk"}
    product = products[animal]
    player.resources[product] = player.resources.get(product, 0) + count
    if player.companion:
        player.companion_morale = min(100, player.companion_morale + 5)
    return f"Collected {count} {product}"


def _sell_resource(player: Player, resource: str, price: int, label: str) -> str:
    count = player.resources.get(resource, 0)
    if count <= 0:
        return f"No {label}"
    player.money += price * count
    player.resources[resource] = 0
    return f"Sold {count} {label}"


def sell_eggs(player: Player) -> str:
    """Sell all collected eggs for cash."""
    return _sell_resource(player, "eggs", 5, "eggs")


def sell_milk(player: Player) -> str:
    """Sell all collected milk for cash."""
    return _sell_resource(player, "milk", 15, "milk")


def train_companion(player: Player) -> str:
    """Spend money and energy to level up a pet companion."""
    if not player.companion:
        return "No pet to train"
    if player.companion_level >= 3:
        return "Pet is fully trained"
    cost = 50
    if player.money < cost:
        return "Need $50"
    if player.energy < 10:
        return "Too tired"
    player.money -= cost
    player.energy -= energy_cost(player, 10)
    player.companion_level += 1
    player.companion_morale = max(0, player.companion_morale - 10)
    if player.companion == "Dog":
        player.defense += 1
    elif player.companion == "Cat":
        player.charisma += 1
    elif player.companion == "Parrot":
        player.intelligence += 1
    elif player.companion == "Llama":
        player.speed += 1
    elif player.companion == "Peacock":
        player.charisma += 1
    elif player.companion == "Rhino":
        player.strength += 1
    return f"{player.companion} reached level {player.companion_level}!"


CRAFT_EXP_BASE = 50

# Base cost for companion ability training
COMPANION_TRAIN_COST = 30


def upgrade_companion_ability(player: Player, index: int, free: bool = False) -> str:
    """Upgrade one of the current companion's abilities.

    Set ``free`` to True to skip cost and energy requirements (used for
    quest rewards).
    """
    if not player.companion:
        return "No pet to train"
    abilities = COMPANION_ABILITIES.get(player.companion)
    if not abilities or index < 0 or index >= len(abilities):
        return "Invalid choice"
    name, _desc, stat = abilities[index]
    levels = player.companion_abilities.setdefault(player.companion, {})
    level = levels.get(name, 0)
    if level >= PERK_MAX_LEVEL:
        return "Ability at max level"
    cost = COMPANION_TRAIN_COST * (level + 1)
    if not free:
        if player.money < cost:
            return f"Need ${cost}"
        if player.energy < 5:
            return "Too tired"
        player.money -= cost
        player.energy -= energy_cost(player, 5)
    levels[name] = level + 1
    if stat == "defense":
        player.defense += 1
    elif stat == "charisma":
        player.charisma += 1
    elif stat == "intelligence":
        player.intelligence += 1
    elif stat == "speed":
        player.speed += 1
    elif stat == "strength":
        player.strength += 1
    elif stat == "tokens":
        player.tokens += 1
    elif stat == "money":
        player.money += 5
    return f"{name} Lv{level + 1} learned!"


def crafting_exp_needed(player: Player, skill: str) -> int:
    """Experience required for next level in a crafting skill."""
    level = player.crafting_skills.get(skill, 1)
    return CRAFT_EXP_BASE * level


def gain_crafting_exp(player: Player, skill: str, amount: int = 5) -> str:
    """Add crafting XP for a skill and handle level ups."""
    xp = player.crafting_exp.get(skill, 0) + amount
    level = player.crafting_skills.get(skill, 1)
    msg = ""
    while xp >= crafting_exp_needed(player, skill):
        xp -= crafting_exp_needed(player, skill)
        level += 1
        msg = f"{skill.capitalize()} leveled to {level}!"
    player.crafting_exp[skill] = xp
    player.crafting_skills[skill] = level
    return msg


def learn_recipe(player: Player, name: str) -> bool:
    """Add a recipe to the player's known list if valid."""
    if name in RECIPES and name not in player.known_recipes:
        player.known_recipes.append(name)
        return True
    return False


def craft_recipe(player: Player, name: str) -> str:
    """Craft an item using a known recipe."""
    recipe = RECIPES.get(name)
    if not recipe:
        return "Unknown recipe"
    if name not in player.known_recipes:
        return "Recipe not known"
    skill = recipe.get("skill", "crafting")
    if recipe.get("level", 1) > player.crafting_skills.get(skill, 1):
        return f"Need {skill.title()} Lv{recipe['level']}"
    reqs = recipe.get("requires", {})
    for res, amt in reqs.items():
        if player.resources.get(res, 0) < amt:
            return f"Need {amt} {res}"
    for res, amt in reqs.items():
        player.resources[res] -= amt
    prod = recipe.get("produces", {})
    item = InventoryItem(**prod)
    player.inventory.append(item)
    lvl_msg = gain_crafting_exp(player, skill)
    return f"Crafted {prod['name']}" + (f"  {lvl_msg}" if lvl_msg else "")


def repair_equipment(player: Player) -> str:
    """Restore durability of all equipped items using 1 metal."""
    if player.resources.get("metal", 0) < 1:
        return "Need 1 metal"
    player.resources["metal"] -= 1
    for item in player.equipment.values():
        if item:
            item.durability = item.max_durability
    lvl_msg = gain_crafting_exp(player, "smithing")
    return "Equipment repaired" + (f"  {lvl_msg}" if lvl_msg else "")
