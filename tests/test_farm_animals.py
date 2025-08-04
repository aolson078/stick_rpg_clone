import pygame
import settings
from entities import Player
from inventory import buy_animal, feed_animals, sell_eggs, sell_milk


def test_chickens_produce_eggs():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.money = 100
    assert "Bought" in buy_animal(player, "chicken")
    assert player.animals["chicken"] == 1
    assert "Collected" in feed_animals(player, "chicken")
    assert player.resources["eggs"] == 1
    assert "Sold" in sell_eggs(player)
    assert player.resources["eggs"] == 0
    assert player.money == 84


def test_cows_produce_milk():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.money = 200
    assert "Bought" in buy_animal(player, "cow")
    assert player.animals["cow"] == 1
    assert "Collected" in feed_animals(player, "cow")
    assert player.resources["milk"] == 1
    assert "Sold" in sell_milk(player)
    assert player.resources["milk"] == 0
    assert player.money == 112
