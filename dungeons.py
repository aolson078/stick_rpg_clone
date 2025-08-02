import random
from typing import List, Dict

from entities import Player, InventoryItem
from combat import FOREST_ENEMIES, fight_custom_enemy


DUNGEON_LOOT: List[InventoryItem] = [
    InventoryItem("Sewer Dagger", "weapon", attack=3, speed=1),
    InventoryItem("Sewer Armor", "chest", defense=3),
    InventoryItem("Old Coin", "consumable"),
]


def generate_dungeon() -> List[Dict[str, int]]:
    """Create a list of random enemies for a dungeon run."""
    rooms = random.randint(2, 4)
    enemies = []
    for _ in range(rooms):
        base = random.choice(FOREST_ENEMIES)
        enemy = {
            "attack": random.randint(max(1, base["attack"] - 1), base["attack"] + 1),
            "defense": random.randint(base["defense"], base["defense"] + 1),
            "speed": random.randint(base["speed"], base["speed"] + 1),
            "health": base["health"] + random.randint(-5, 5),
            "reward": base["reward"],
        }
        enemies.append(enemy)
    return enemies


def explore_dungeon(player: Player) -> str:
    """Run a short procedural dungeon and return the result message."""
    if player.energy < 10:
        return "Too tired to explore!"
    enemies = generate_dungeon()
    for enemy in enemies:
        result = fight_custom_enemy(player, enemy)
        if "lost" in result:
            return "You were defeated in the dungeon!"
    loot = random.choice(DUNGEON_LOOT)
    player.inventory.append(loot)
    return f"Dungeon cleared! You found {loot.name}"
