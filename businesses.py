"""Business purchasing, upgrades, staffing, and profit calculations."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from entities import Player
from combat import energy_cost
import factions


@dataclass
class BusinessType:
    """Definition for a type of business."""
    cost: int
    base_profit: int
    upgrade_to: Optional[str] = None
    upgrade_cost: int = 0
    staff_cost: int = 0


# Information about each business type and upgrade path
BUSINESS_DATA: Dict[str, BusinessType] = {
    "Stall": BusinessType(cost=500, base_profit=25, upgrade_to="Store", upgrade_cost=1500, staff_cost=5),
    "Store": BusinessType(cost=2000, base_profit=80, upgrade_to="Restaurant", upgrade_cost=5000, staff_cost=20),
    "Restaurant": BusinessType(cost=8000, base_profit=200, upgrade_to=None, upgrade_cost=0, staff_cost=35),
}

# Ordered list of business names for menu display
BUSINESS_CATALOG: List[str] = ["Stall", "Store", "Restaurant"]

# Backwards compatible list of tuples for legacy code (name, cost, base profit)
BUSINESSES: List[Tuple[str, int, int]] = [
    (name, BUSINESS_DATA[name].cost, BUSINESS_DATA[name].base_profit) for name in BUSINESS_CATALOG
]


def buy_business(player: Player, index: int) -> str:
    """Purchase a new business by catalog index."""
    if index < 0 or index >= len(BUSINESS_CATALOG):
        return "Invalid choice"
    name = BUSINESS_CATALOG[index]
    data = BUSINESS_DATA[name]
    if name in player.businesses:
        return "Already owned"
    if player.money < data.cost:
        return "Not enough money!"
    player.money -= data.cost
    player.businesses[name] = data.base_profit
    player.business_bonus[name] = 0
    player.business_staff[name] = 0
    player.business_reputation[name] = 0
    player.business_skill[name] = 0
    return f"Bought {name}"


def manage_business(player: Player, name: str) -> str:
    """Simple management minigame to boost profits via charisma."""
    if name not in player.businesses:
        return "No such business"
    if player.energy < 5:
        return "Too tired"
    player.energy -= energy_cost(player, 5)
    chance = player.charisma + random.randint(0, 10)
    rewards = factions.business_rewards(player)
    if "Loyal Customers" in rewards:
        chance += 5
    if chance > 10:
        bonus = random.randint(10, 30)
        if "Investor" in rewards:
            bonus = int(bonus * 1.5)
        player.business_bonus[name] = player.business_bonus.get(name, 0) + bonus
        return f"Great promotion! +${bonus}"
    return "Slow day at the shop"


def run_marketing_campaign(player: Player, name: str) -> str:
    """Spend money to temporarily boost a business's reputation."""
    if name not in player.businesses:
        return "No such business"
    cost = 100
    if player.money < cost:
        return "Not enough money!"
    player.money -= cost
    boost = random.randint(10, 30)
    player.business_reputation[name] = player.business_reputation.get(name, 0) + boost
    return f"Campaign raised rep by {boost}"


def train_staff(player: Player, name: str) -> str:
    """Train staff to temporarily lower robbery risk."""
    if name not in player.businesses:
        return "No such business"
    if player.energy < 5:
        return "Too tired"
    player.energy -= energy_cost(player, 5)
    gain = random.randint(1, 3)
    player.business_skill[name] = player.business_skill.get(name, 0) + gain
    return f"Staff trained +{gain}"


def upgrade_business(player: Player, name: str) -> str:
    """Upgrade a business to its next tier if possible."""
    if name not in player.businesses:
        return "No such business"
    current = BUSINESS_DATA.get(name)
    if not current or not current.upgrade_to:
        return "No upgrade available"
    if player.money < current.upgrade_cost:
        return "Not enough money!"
    next_name = current.upgrade_to
    next_data = BUSINESS_DATA[next_name]
    player.money -= current.upgrade_cost
    bonus = player.business_bonus.pop(name, 0)
    staff = player.business_staff.pop(name, 0)
    reputation = player.business_reputation.pop(name, 0)
    skill = player.business_skill.pop(name, 0)
    del player.businesses[name]
    player.businesses[next_name] = next_data.base_profit
    player.business_bonus[next_name] = bonus
    player.business_staff[next_name] = staff
    player.business_reputation[next_name] = reputation
    player.business_skill[next_name] = skill
    return f"Upgraded {name} to {next_name}"


def hire_staff(player: Player, name: str, count: int = 1) -> str:
    """Hire staff to work at a business."""
    if name not in player.businesses:
        return "No such business"
    player.business_staff[name] = player.business_staff.get(name, 0) + max(0, count)
    return f"Hired {count} staff for {name}"


def collect_profits(player: Player) -> int:
    """Return and add profits from all owned businesses.

    Profits are influenced by charisma and staff. Each staff member adds
    a small profit boost but also incurs wages. There is also a chance of a
    robbery which results in no profit for that business on that day.
    """
    total = 0
    for name, base in player.businesses.items():
        data = BUSINESS_DATA.get(name)
        bonus = player.business_bonus.get(name, 0)
        staff = player.business_staff.get(name, 0)
        reputation = player.business_reputation.get(name, 0)
        skill = player.business_skill.get(name, 0)
        staff_profit = staff * 10
        wages = staff * (data.staff_cost if data else 0)
        profit = base + player.charisma * 2 + bonus + staff_profit - wages + reputation
        # Risk of robbery mitigated by staff presence and skill
        risk = max(0.1 - 0.02 * staff - 0.02 * skill, 0.02)
        if random.random() < risk:
            profit = 0
        total += profit
        player.business_bonus[name] = 0
        player.business_reputation[name] = 0
        player.business_skill[name] = 0
    player.money += total
    return total

