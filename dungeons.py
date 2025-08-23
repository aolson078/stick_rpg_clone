import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from entities import InventoryItem, Player
from combat import FOREST_ENEMIES, fight_custom_enemy


@dataclass
class Room:
    """A single dungeon room with enemies, optional trap and exits."""

    enemies: List[Dict[str, int]]
    trap: Optional[str]
    exits: List[int]


DUNGEON_LOOT: List[InventoryItem] = [
    InventoryItem("Sewer Dagger", "weapon", attack=3, speed=1),
    InventoryItem("Sewer Armor", "chest", defense=3),
    InventoryItem("Old Coin", "consumable"),
]

# Rewards for rooms that only contain traps or puzzles
TRAP_LOOT: List[InventoryItem] = [
    InventoryItem("Healing Herb", "consumable"),
    InventoryItem("Shiny Pebble", "consumable"),
]


TRAPS = ["spike trap", "pit trap", "ancient puzzle"]


def _random_enemy() -> Dict[str, int]:
    base = random.choice(FOREST_ENEMIES)
    enemy = {
        "attack": random.randint(max(1, base["attack"] - 1), base["attack"] + 1),
        "defense": random.randint(base["defense"], base["defense"] + 1),
        "speed": random.randint(base["speed"], base["speed"] + 1),
        "health": base["health"] + random.randint(-5, 5),
        "reward": base["reward"],
    }
    return enemy


def generate_dungeon() -> List[Room]:
    """Create a graph of connected rooms with random traps or puzzles."""

    room_count = random.randint(2, 4)
    rooms: List[Room] = []
    for _ in range(room_count):
        enemy_count = random.randint(0, 2)
        enemies = [_random_enemy() for _ in range(enemy_count)]
        trap = random.choice(TRAPS + [None])
        rooms.append(Room(enemies=enemies, trap=trap, exits=[]))

    # Connect rooms linearly first
    for i in range(room_count - 1):
        rooms[i].exits.append(i + 1)
        rooms[i + 1].exits.append(i)

    # Add a few random extra connections for branching paths
    for i in range(room_count):
        if random.random() < 0.3:
            other = random.randint(0, room_count - 1)
            if other != i and other not in rooms[i].exits:
                rooms[i].exits.append(other)
                rooms[other].exits.append(i)
    return rooms


def explore_dungeon(player: Player, choose_action: Optional[Callable] = None) -> str:
    """Run a short procedural dungeon and return the result message."""

    if player.energy < 10:
        return "Too tired to explore!"

    dungeon = generate_dungeon()
    current = 0
    visited = set()

    def auto_choice(kind, options=None):
        if kind == "trap":
            return "disarm"
        if kind == "enemy":
            return "fight"
        if kind == "exit":
            for ex in options:
                if ex not in visited:
                    return ex
            return options[0] if options else None

    if choose_action is None:
        choose_action = auto_choice

    while True:
        room = dungeon[current]
        visited.add(current)

        # Handle traps or puzzles
        if room.trap:
            action = choose_action("trap", room)
            if action == "disarm":
                chance = min(0.9, 0.5 + player.speed * 0.05)
                if random.random() <= chance:
                    if not room.enemies:
                        reward = random.choice(TRAP_LOOT)
                        player.inventory.append(reward)
                else:
                    player.health -= 5
                    if player.health <= 0:
                        return "You were defeated in the dungeon!"
            else:
                player.health -= 5
                if player.health <= 0:
                    return "You were defeated in the dungeon!"

        # Combat encounters
        for enemy in room.enemies:
            action = choose_action("enemy", enemy)
            if action == "flee" and random.random() < 0.5:
                continue
            result = fight_custom_enemy(player, enemy)
            if "lost" in result:
                return "You were defeated in the dungeon!"

        # Check for completion
        if current == len(dungeon) - 1:
            loot = random.choice(DUNGEON_LOOT)
            player.inventory.append(loot)
            return f"Dungeon cleared! You found {loot.name}"

        # Choose next room
        next_room = choose_action("exit", room.exits)
        if next_room is None:
            loot = random.choice(DUNGEON_LOOT)
            player.inventory.append(loot)
            return f"Dungeon cleared! You found {loot.name}"
        current = next_room
