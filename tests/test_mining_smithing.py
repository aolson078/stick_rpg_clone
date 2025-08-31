import pygame
import settings
from entities import Player
from inventory import mine_ore, smelt_ore


def test_mining_adds_ore_and_exp():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    mine_ore(player)
    assert player.resources["ore"] == 1
    assert player.crafting_exp["mining"] == 5
    assert player.crafting_skills.get("mining", 1) == 1


def test_smelt_ore_converts_and_grants_exp():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    assert smelt_ore(player) == "Need 1 ore"
    player.resources["ore"] = 1
    smelt_ore(player)
    assert player.resources["ore"] == 0
    assert player.resources["metal"] == 1
    assert player.crafting_exp["smithing"] == 5
    assert player.crafting_skills.get("smithing", 1) == 1
