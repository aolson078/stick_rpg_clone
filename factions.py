"""Faction and reputation helpers."""
from typing import Dict

from entities import Player

FACTIONS = ["mayor", "business", "gang"]


def change_reputation(player: Player, faction: str, amount: int) -> None:
    """Adjust reputation with a faction and clamp between -100 and 100."""
    if faction not in FACTIONS:
        return
    rep = player.reputation.get(faction, 0) + amount
    player.reputation[faction] = max(-100, min(100, rep))


def business_price(player: Player, cost: int) -> int:
    """Return item cost adjusted by business reputation."""
    rep = player.reputation.get("business", 0)
    multiplier = 1.0
    if rep >= 50:
        multiplier = 0.8
    elif rep >= 20:
        multiplier = 0.9
    elif rep <= -50:
        multiplier = 1.25
    elif rep <= -20:
        multiplier = 1.1
    return int(round(cost * multiplier))
