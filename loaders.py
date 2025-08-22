import json
import os
import pygame
from typing import List, Dict

from entities import Building, Quest, SideQuest
from inventory import HOME_UPGRADES, COMPANION_ABILITIES, upgrade_companion_ability
import settings
from tilemap import BUS_STOP_BUILDINGS


def load_buildings(path: str = "data/buildings.json") -> List[Building]:
    """Load building definitions from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    data.extend(BUS_STOP_BUILDINGS)
    buildings: List[Building] = []
    for b in data:
        rect = pygame.Rect(*b["rect"])
        name = b["name"]
        btype = b["type"]
        image = None
        if btype != "bus_stop":
            filename = settings.BUILDING_SPRITES.get(
                btype, settings.BUILDING_SPRITES["default"]
            )
            img_path = os.path.join(settings.BUILDING_IMAGE_DIR, filename)
            try:
                image = pygame.image.load(img_path).convert_alpha()
            except pygame.error:
                image = None
        buildings.append(Building(rect, name, btype, image))
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
        dialogue = sq.get("dialogue", [])
        objectives = sq.get("objectives", [])
        comp = sq.get("companion")
        reward_cfg = sq.get("reward", 0)
        if isinstance(reward_cfg, dict) and reward_cfg.get("ability") and comp:
            ability = reward_cfg["ability"]

            def reward_func(p, c=comp, abil=ability):
                if p.companion != c:
                    return
                abilities = COMPANION_ABILITIES.get(c, [])
                idx = next((i for i, a in enumerate(abilities) if a[0] == abil), None)
                if idx is not None:
                    upgrade_companion_ability(p, idx, free=True)

        else:
            amt = reward_cfg if isinstance(reward_cfg, (int, float)) else 0

            def reward_func(p, amt=amt):
                setattr(p, "money", p.money + amt)

        side_list.append(
            SideQuest(name, desc, target, reward_func, dialogue, objectives)
        )
    return {q.name: q for q in side_list}
