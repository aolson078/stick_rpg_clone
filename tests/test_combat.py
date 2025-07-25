import pygame
import settings
from entities import Player
from combat import fight_brawler, BRAWLER_COUNT


def test_fight_brawler_too_tired():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 5
    result = fight_brawler(player)
    assert result == "Too tired to fight!"


def test_fight_brawler_no_challengers():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.brawls_won = BRAWLER_COUNT
    result = fight_brawler(player)
    assert result == "No challengers remain"

