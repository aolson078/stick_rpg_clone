import json
import pygame
from typing import List, Dict

from entities import Building, Quest, SideQuest
from inventory import HOME_UPGRADES


def load_buildings(path: str = "data/buildings.json") -> List[Building]:
    """Load building definitions from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    buildings = [
        Building(pygame.Rect(*b["rect"]), b["name"], b["type"]) for b in data
    ]
    return buildings


# Quest check functions map by index

def _quest_check(idx: int, player) -> bool:
    if idx == 0:
        return player.money >= 200
    if idx == 1:
        return player.strength >= 5
    if idx == 2:
        return player.intelligence >= 5
    if idx == 3:
        return player.money >= 300
    if idx == 4:
        return player.strength >= 5
    if idx == 5:
        return player.enemies_defeated >= 3
    if idx == 6:
        return set(player.home_upgrades) == {u[0] for u in HOME_UPGRADES}
    return False


def load_quests(path: str = "data/quests.json") -> List[Quest]:
    """Load quests from JSON, pairing with predefined checks."""
    with open(path) as f:
        data = json.load(f)
    quests: List[Quest] = []
    for i, q in enumerate(data):
        desc = q.get("description", "")
        next_idx = q.get("next_index")
        quests.append(
            Quest(desc, lambda p, _i=i: _quest_check(_i, p), next_index=next_idx)
        )
    return quests


def load_sidequests(path: str = "data/sidequests.json") -> Dict[str, SideQuest]:
    """Load side quest definitions and return mapping by name."""
    with open(path) as f:
        data = json.load(f)
    side_list = []
    for sq in data:
        name = sq["name"]
        desc = sq["description"]
        target = sq["target"]
        reward_amt = sq.get("reward", 0)
        side_list.append(
            SideQuest(name, desc, target, lambda p, amt=reward_amt: setattr(p, "money", p.money + amt))
        )
    return {q.name: q for q in side_list}
