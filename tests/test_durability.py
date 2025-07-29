import pygame
import settings
from entities import Player, InventoryItem
from combat import fight_enemy
from inventory import repair_equipment


def test_durability_decreases_after_combat():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    weapon = InventoryItem("Test Sword", "weapon", attack=5)
    player.equipment["weapon"] = weapon
    # make player strong to end fight quickly
    player.strength = 20
    fight_enemy(player)
    assert weapon.durability < weapon.max_durability


def test_repair_equipment_restores_durability():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    weapon = InventoryItem("Test Sword", "weapon", attack=5)
    player.equipment["weapon"] = weapon
    weapon.durability = 50
    player.resources["metal"] = 1
    msg = repair_equipment(player)
    assert weapon.durability == weapon.max_durability
    assert "Equipment repaired" in msg
