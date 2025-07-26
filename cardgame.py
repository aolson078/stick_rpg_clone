"""Simple trading card duel mini-game."""

from __future__ import annotations
import random
from typing import List

from entities import Player
from quests import CARD_NAMES

# Extra rare cards that can only be obtained from duels
RARE_CARDS: List[str] = ["Phoenix", "Golem"]


def _card_power(name: str) -> int:
    """Return a basic power score for a card name."""
    if name in CARD_NAMES:
        return CARD_NAMES.index(name) + 1
    if name in RARE_CARDS:
        return len(CARD_NAMES) + RARE_CARDS.index(name) + 2
    return 1


def card_duel(player: Player) -> str:
    """Duel an NPC using random cards."""
    if player.energy < 5:
        return "Too tired to duel!"
    player.energy -= 5

    npc_cards = random.sample(CARD_NAMES, k=3)
    deck = player.cards if player.cards else CARD_NAMES
    player_cards = random.sample(deck, k=3)

    player_score = sum(_card_power(c) for c in player_cards)
    npc_score = sum(_card_power(c) for c in npc_cards)

    if player_score >= npc_score:
        player.card_duels_won += 1
        pool = [c for c in CARD_NAMES if c not in player.cards]
        if not pool and random.random() < 0.3:
            pool = [c for c in RARE_CARDS if c not in player.cards]
        if pool:
            reward = random.choice(pool)
            player.cards.append(reward)
            return f"You won the duel and got {reward}!"
        return "You won the duel!"

    return "You lost the duel."
