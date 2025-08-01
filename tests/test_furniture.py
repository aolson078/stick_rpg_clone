import pygame
import settings
from entities import Player, InventoryItem
from helpers import init_furniture_positions, sleep


def test_furniture_bonus():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    init_furniture_positions(player)
    player.furniture["slot1"] = InventoryItem("Decor Chair", "furniture")
    before = player.charisma
    sleep(player)
    assert player.charisma == before + 1
