"""Faction and reputation helpers."""
from typing import Dict, List

from entities import Player

FACTIONS = ["mayor", "business", "gang"]


def change_reputation(player: Player, faction: str, amount: int) -> None:
    """Adjust reputation with a faction and clamp between -100 and 100."""
    if faction not in FACTIONS:
        return
    rep = player.reputation.get(faction, 0) + amount
    player.reputation[faction] = max(-100, min(100, rep))


def get_business_discount(player: Player) -> float:
    """Return cost multiplier based on business reputation."""
    rep = player.reputation.get("business", 0)
    if rep >= 50:
        return 0.8
    if rep >= 20:
        return 0.9
    if rep <= -50:
        return 1.25
    if rep <= -20:
        return 1.1
    return 1.0


def business_price(player: Player, cost: int) -> int:
    """Return item cost adjusted by business reputation."""
    return int(round(cost * get_business_discount(player)))


def mayor_rewards(player: Player) -> List[str]:
    """Return rewards unlocked from mayor reputation."""
    rep = player.reputation.get("mayor", 0)
    rewards: List[str] = []
    if rep >= 50:
        rewards.append("City Key")
    elif rep >= 20:
        rewards.append("Town Hall Access")
    return rewards


def business_rewards(player: Player) -> List[str]:
    """Return rewards unlocked from business reputation."""
    rep = player.reputation.get("business", 0)
    rewards: List[str] = []
    if rep >= 50:
        rewards.append("Investor")
    elif rep >= 20:
        rewards.append("Loyal Customers")
    return rewards


def gang_rewards(player: Player) -> List[str]:
    """Return rewards unlocked from gang reputation."""
    rep = player.reputation.get("gang", 0)
    rewards: List[str] = []
    if rep >= 50:
        rewards.append("Gang Backup")
    elif rep >= 20:
        rewards.append("Black Market")
    return rewards
