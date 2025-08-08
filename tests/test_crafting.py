import pygame
import settings
from entities import Player
from inventory import crafting_exp_needed, CRAFT_EXP_BASE, craft_recipe


def test_crafting_exp_needed_level1():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    assert crafting_exp_needed(player) == CRAFT_EXP_BASE


def test_crafting_exp_needed_higher_level():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.crafting_level = 3
    assert crafting_exp_needed(player) == CRAFT_EXP_BASE * 3


def test_craft_requires_known_recipe():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.resources["herbs"] = 5
    # Unknown recipe cannot be crafted
    msg = craft_recipe(player, "Health Potion")
    assert msg == "Recipe not known"
    # Learn recipe and craft
    player.known_recipes.append("Health Potion")
    msg = craft_recipe(player, "Health Potion")
    assert "Crafted Health Potion" in msg
    assert player.resources["herbs"] == 3
    assert any(it.name == "Health Potion" for it in player.inventory)

