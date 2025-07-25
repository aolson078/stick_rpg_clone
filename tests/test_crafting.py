import pygame
import settings
from entities import Player
from inventory import crafting_exp_needed, CRAFT_EXP_BASE


def test_crafting_exp_needed_level1():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    assert crafting_exp_needed(player) == CRAFT_EXP_BASE


def test_crafting_exp_needed_higher_level():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.crafting_level = 3
    assert crafting_exp_needed(player) == CRAFT_EXP_BASE * 3

