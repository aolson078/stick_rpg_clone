import random
import random
import pygame
import settings
from entities import Player
import dungeons
from dungeons import explore_dungeon, Room


def test_explore_dungeon_rewards_loot():
    random.seed(0)
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 100
    player.strength = 10
    player.defense = 5
    count = len(player.inventory)
    msg = explore_dungeon(player)
    assert "Dungeon cleared" in msg
    # At least one reward should be granted
    assert len(player.inventory) >= count + 1


def test_explore_dungeon_tired():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 5
    msg = explore_dungeon(player)
    assert msg == "Too tired to explore!"


def test_trap_room_reward(monkeypatch):
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 100

    def fake_gen():
        return [
            Room(enemies=[], trap="spike trap", exits=[1]),
            Room(enemies=[], trap=None, exits=[]),
        ]

    monkeypatch.setattr(dungeons, "generate_dungeon", fake_gen)
    monkeypatch.setattr(dungeons.random, "random", lambda: 0.0)
    count = len(player.inventory)
    msg = explore_dungeon(player)
    assert "Dungeon cleared" in msg
    # Trap loot plus final loot
    assert len(player.inventory) == count + 2
