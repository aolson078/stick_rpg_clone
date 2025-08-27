"""Tests for inventory sorting helper."""

import pygame

from entities import Player, InventoryItem
import settings
from inventory import sort_inventory


def make_player():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.inventory = [
        InventoryItem("Sword", "weapon", attack=5),
        InventoryItem("Apple", "consumable"),
        InventoryItem("Bow", "weapon", attack=3, speed=1),
    ]
    return player


def test_sort_by_name():
    player = make_player()
    sort_inventory(player, "name")
    assert [i.name for i in player.inventory] == ["Apple", "Bow", "Sword"]


def test_sort_by_type():
    player = make_player()
    sort_inventory(player, "type")
    assert [i.name for i in player.inventory] == ["Apple", "Bow", "Sword"]


def test_sort_by_stat():
    player = make_player()
    sort_inventory(player, "stat")
    assert [i.name for i in player.inventory] == ["Sword", "Bow", "Apple"]
