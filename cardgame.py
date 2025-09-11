"""Simple trading card duel mini-game with deck support."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from entities import Player
from quests import CARD_NAMES

# Extra rare cards that can only be obtained from duels or boosters
RARE_CARDS: List[str] = ["Phoenix", "Golem"]


@dataclass
class Card:
    """Basic card data used during duels."""

    name: str
    attack: int
    defense: int = 0
    effect: Optional[str] = None


CARD_DATA = {name: {"attack": i + 1, "defense": (i + 1) // 2} for i, name in enumerate(CARD_NAMES)}
for i, name in enumerate(RARE_CARDS, start=len(CARD_NAMES) + 1):
    CARD_DATA[name] = {"attack": i + 1, "defense": (i + 1) // 2}


def _make_card(name: str) -> Card:
    data = CARD_DATA.get(name, {"attack": 1, "defense": 0})
    return Card(name, data["attack"], data.get("defense", 0), data.get("effect"))


@dataclass
class Deck:
    """A deck containing up to 30 cards with draw and discard piles."""

    names: List[str]
    draw_pile: List[Card] = field(init=False)
    discard_pile: List[Card] = field(default_factory=list)

    def __post_init__(self) -> None:
        limited = self.names[:30]
        self.draw_pile = [_make_card(n) for n in limited]
        random.shuffle(self.draw_pile)

    def draw(self) -> Optional[Card]:
        if not self.draw_pile:
            if not self.discard_pile:
                return None
            self.draw_pile = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.draw_pile)
        return self.draw_pile.pop()

    def discard(self, card: Card) -> None:
        self.discard_pile.append(card)

    def add(self, name: str) -> None:
        if len(self.draw_pile) + len(self.discard_pile) >= 30:
            return
        card = _make_card(name)
        self.draw_pile.append(card)


def open_booster_pack(player: Player, count: int = 3) -> List[str]:
    """Add ``count`` random cards to the player's collection."""

    pool = CARD_NAMES + RARE_CARDS
    rewards: List[str] = []
    for _ in range(count):
        name = random.choice(pool)
        player.cards.append(name)
        rewards.append(name)
    return rewards


def card_duel(player: Player) -> str:
    """Duel an NPC using a turn-based match loop."""

    if player.energy < 5:
        return "Too tired to duel!"
    player.energy -= 5

    player_names = player.deck or player.cards or CARD_NAMES
    npc_names = random.sample(CARD_NAMES, k=min(30, len(CARD_NAMES)))

    p_deck = Deck(player_names)
    n_deck = Deck(npc_names)

    p_hand = [p_deck.draw() for _ in range(5)]
    n_hand = [n_deck.draw() for _ in range(5)]

    p_health = 20
    n_health = 20

    while p_health > 0 and n_health > 0 and (p_hand or p_deck.draw_pile) and (
        n_hand or n_deck.draw_pile
    ):
        p_card = p_hand.pop(0) if p_hand else p_deck.draw()
        n_card = n_hand.pop(0) if n_hand else n_deck.draw()
        if not p_card or not n_card:
            break
        n_damage = max(p_card.attack - n_card.defense, 0)
        p_damage = max(n_card.attack - p_card.defense, 0)
        n_health -= n_damage
        p_health -= p_damage
        p_deck.discard(p_card)
        n_deck.discard(n_card)
        if draw := p_deck.draw():
            p_hand.append(draw)
        if draw := n_deck.draw():
            n_hand.append(draw)

    if p_health > n_health:
        player.card_duels_won += 1
        reward = open_booster_pack(player, 1)[0]
        return f"You won the duel and got {reward}!"
    return "You lost the duel."
