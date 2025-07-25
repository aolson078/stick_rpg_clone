"""Business purchasing and profit calculations."""
from __future__ import annotations
from typing import List, Tuple
import random

from entities import Player
from combat import energy_cost

# (name, cost, base daily profit)
BUSINESSES: List[Tuple[str, int, int]] = [
    ("Stall", 500, 25),
    ("Store", 2000, 80),
]


def buy_business(player: Player, index: int) -> str:
    """Purchase a new business by index."""
    if index < 0 or index >= len(BUSINESSES):
        return "Invalid choice"
    name, cost, profit = BUSINESSES[index]
    if name in player.businesses:
        return "Already owned"
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    player.businesses[name] = profit
    player.business_bonus[name] = 0
    return f"Bought {name}"


def manage_business(player: Player, name: str) -> str:
    """Simple management minigame to boost profits."""
    if name not in player.businesses:
        return "No such business"
    if player.energy < 5:
        return "Too tired"
    player.energy -= energy_cost(player, 5)
    chance = player.charisma + random.randint(0, 10)
    if chance > 10:
        bonus = random.randint(10, 30)
        player.business_bonus[name] = player.business_bonus.get(name, 0) + bonus
        return f"Great promotion! +${bonus}"
    return "Slow day at the shop"


def collect_profits(player: Player) -> int:
    """Return and add profits from all owned businesses."""
    total = 0
    for name, base in player.businesses.items():
        bonus = player.business_bonus.get(name, 0)
        profit = base + player.charisma * 2 + bonus
        total += profit
        player.business_bonus[name] = 0
    player.money += total
    return total
