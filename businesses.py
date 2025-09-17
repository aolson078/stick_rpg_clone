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


def _future_margin(data: BusinessType) -> int:
    """Return the upfront margin required for a futures position."""

    return max(50, int(data.base_profit * 0.6))


def schedule_future_contract(player: Player, name: str) -> str:
    """Arrange a futures contract for the selected business."""

    if name not in player.businesses:
        return "No such business"
    if name in player.business_futures:
        contract = player.business_futures[name]
        due = contract.get("day_due", player.day)
        return f"Existing future matures day {due}"

    data = BUSINESS_DATA.get(name)
    if not data:
        return "No market data"

    margin = _future_margin(data)
    if player.money < margin:
        return f"Need ${margin} margin to tempt the futures clerks"

    player.money -= margin

    roll_bonus = random.randint(0, 8)
    charisma_score = player.charisma + roll_bonus
    days_out = random.randint(2, 4)
    day_due = player.day + days_out

    if charisma_score < 8:
        risk = "speculative"
        payout = random.randint(-data.base_profit * 3, data.base_profit * 4)
        reputation_bonus = 6
        flavour = (
            f"A shadow broker for {name} scribbles a paradox hedge while laughing at causality."
        )
    elif charisma_score < 14:
        risk = "hedged"
        payout = random.randint(int(data.base_profit * 0.5), int(data.base_profit * 1.5))
        reputation_bonus = 0
        flavour = (
            f"You secure a measured hedge for {name}, wagering reality will mostly behave."
        )
    else:
        risk = "premium"
        payout = random.randint(int(data.base_profit * 1.5), data.base_profit * 3)
        reputation_bonus = 2
        flavour = (
            f"Your charisma dazzles the exchange, granting {name} a premium timeline arbitrage."
        )

    contract = {
        "payout": int(payout),
        "day_due": day_due,
        "risk": risk,
        "margin": margin,
        "flavour": flavour,
        "reputation_bonus": reputation_bonus,
        "charisma_score": charisma_score,
    }
    player.business_futures[name] = contract

    summary = (
        f"{flavour} Margin ${margin} committed for a projected ${payout} on day {day_due}."
    )
    player.business_future_log.append(summary)
    return summary


def _resolve_future_contract(player: Player, name: str) -> tuple[int, str]:
    """Remove and settle a futures contract, returning payout and narration."""

    contract = player.business_futures.pop(name, None)
    if not contract:
        return 0, "No futures contract found"

    payout = int(contract.get("payout", 0))
    risk = contract.get("risk", "hedged")
    flavour = contract.get("flavour", f"The future of {name} unravels.")
    message_parts = [flavour]

    if payout >= 0:
        message_parts.append(f"The {risk} futures on {name} crystallise ${payout}.")
        if risk == "speculative" and payout > 0:
            rep_gain = contract.get("reputation_bonus", 5)
            player.reputation["business"] = player.reputation.get("business", 0) + rep_gain
            message_parts.append(f" Brokers applaud your audacity (+{rep_gain} business rep).")
        elif risk != "hedged":
            rep_gain = contract.get("reputation_bonus", 0)
            if rep_gain:
                player.reputation["business"] = player.reputation.get("business", 0) + rep_gain
                message_parts.append(f" Reputation nudges up by {rep_gain}.")
        message_parts.append("Reality briefly cooperates.")
    else:
        loss = abs(payout)
        message_parts.append(
            f"The {risk} futures on {name} implode, vaporising ${loss} and smudging the ledgers."
        )
        message_parts.append("Accountants whisper about negative space balance sheets.")

    player.money += payout

    message = " ".join(message_parts)
    player.business_future_log.append(message)
    return payout, message


def cash_out_future(player: Player, name: str) -> str:
    """Attempt to cash out a futures contract if it has matured."""

    if name not in player.businesses:
        return "No such business"
    contract = player.business_futures.get(name)
    if not contract:
        return "No futures contract active"
    if player.day < contract.get("day_due", player.day):
        return f"Contract matures day {contract['day_due']}; patience may yet pay"

    _, message = _resolve_future_contract(player, name)
    return message


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


def random_event(player: Player, name: str) -> tuple[int, str]:
    """Apply a random business event and return its profit modifier and message.

    The event can positively or negatively impact daily profits and also adjust
    the player's reputation with the business faction.  The returned tuple is
    ``(profit_delta, message)`` where ``profit_delta`` should be added to the
    day's profit and ``message`` describes the event (empty if no event).
    """

    roll = random.random()
    message = ""
    profit_delta = 0
    rep_delta = 0

    # 10% chance of a health inspection resulting in fines
    if roll < 0.1:
        profit_delta -= 20
        rep_delta -= 5
        message = f"Inspection at {name} resulted in a fine"
    # 10% chance of a sales boom
    elif roll < 0.2:
        profit_delta += 50
        rep_delta += 5
        message = f"{name} saw a huge sales boom"
    # 10% chance of staff strike
    elif roll < 0.3:
        profit_delta -= 30
        rep_delta -= 5
        message = f"Workers at {name} went on strike"

    if rep_delta:
        player.reputation["business"] = player.reputation.get("business", 0) + rep_delta

    return profit_delta, message


def collect_profits(player: Player) -> tuple[int, list[str]]:
    """Return and add profits from all owned businesses.

    Profits are influenced by charisma and staff. Each staff member adds
    a small profit boost but also incurs wages. There is also a chance of a
    robbery which results in no profit for that business on that day.  Random
    events may further modify profits or reputation and their messages are
    returned for display.
    """
    total = 0
    events: List[str] = []

    for name, contract in list(player.business_futures.items()):
        if player.day >= contract.get("day_due", player.day):
            _, message = _resolve_future_contract(player, name)
            if message:
                events.append(message)

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
        robbed = False
        if random.random() < risk:
            profit = 0
            robbed = True
        if not robbed:
            delta, msg = random_event(player, name)
            profit += delta
            if msg:
                events.append(msg)
        total += profit
        player.business_bonus[name] = 0
        player.business_reputation[name] = 0
        player.business_skill[name] = 0
    player.money += total
    return total, events

