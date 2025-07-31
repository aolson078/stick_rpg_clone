import random
import pygame
import settings
from entities import Player
from inventory import get_shop_price, SHOP_ITEMS


def make_player():
    return Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))


def test_shop_price_base():
    player = make_player()
    base = SHOP_ITEMS[0][1]
    assert get_shop_price(player, 0) == base


def test_shop_price_fluctuates():
    player = make_player()
    player.day = 2
    player.season = "Winter"
    r = random.Random(player.day).random()
    expected = int(round(SHOP_ITEMS[0][1] * 1.2 * (0.8 + r * 0.4)))
    assert get_shop_price(player, 0) == expected
