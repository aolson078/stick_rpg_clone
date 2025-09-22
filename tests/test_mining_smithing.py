import pygame
import settings
from entities import Player
from inventory import mine_ore, smelt_ore
def test_shallow_mining_grants_byproducts_and_exp():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    message = mine_ore(player)

    assert player.resources["ore"] == 1
    assert player.resources["stone"] == 1
    assert player.crafting_exp["mining"] == 5
    assert player.crafting_skills.get("mining", 1) == 1
    assert "Mined 1 ore" in message
    assert "Found 1 stone" in message


def test_richer_vein_requires_skill():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))

    message = mine_ore(player, vein="rich")

    assert message == "Need Mining Lv3"
    assert player.resources["ore"] == 0
    assert player.resources["stone"] == 0
    assert player.resources["gems"] == 0


def test_deep_vein_scales_rewards_with_level():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.crafting_skills["mining"] = 5

    message = mine_ore(player, swings=2, vein="deep")

    assert player.resources["ore"] == 6
    assert player.resources["stone"] == 6
    assert player.resources["gems"] == 2
    assert player.crafting_exp["mining"] == 40
    assert player.crafting_skills["mining"] == 5
    assert "Mined 6 ore" in message
    assert "stone" in message and "gems" in message


def test_smelt_ore_converts_and_grants_exp():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    assert smelt_ore(player) == "Need 1 ore"
    player.resources["ore"] = 1
    smelt_ore(player)
    assert player.resources["ore"] == 0
    assert player.resources["metal"] == 1
    assert player.crafting_exp["smithing"] == 5
    assert player.crafting_skills.get("smithing", 1) == 1
