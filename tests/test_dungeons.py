import random
import pygame
import settings
from entities import Player
from dungeons import explore_dungeon


def test_explore_dungeon_rewards_loot():
    random.seed(0)
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 100
    player.strength = 10
    player.defense = 5
    count = len(player.inventory)
    msg = explore_dungeon(player)
    assert "Dungeon cleared" in msg
    assert len(player.inventory) == count + 1


def test_explore_dungeon_tired():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 5
    msg = explore_dungeon(player)
    assert msg == "Too tired to explore!"
