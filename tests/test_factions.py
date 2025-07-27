import pygame
import settings
from entities import Player
from inventory import buy_shop_item
from factions import change_reputation, business_price


def make_player():
    return Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))


def test_change_reputation_clamped():
    player = make_player()
    change_reputation(player, "mayor", 120)
    assert player.reputation["mayor"] == 100
    change_reputation(player, "mayor", -250)
    assert player.reputation["mayor"] == -100


def test_business_price_adjustment():
    player = make_player()
    change_reputation(player, "business", 50)
    assert business_price(player, 100) == 80
    change_reputation(player, "business", -120)
    assert business_price(player, 100) == 125


def test_buy_shop_item_discount():
    player = make_player()
    change_reputation(player, "business", 50)
    player.money = 5
    msg = buy_shop_item(player, 0)  # Cola costs 3
    assert msg == "Bought Cola"
    # cost after 20% discount should be 2
    assert player.money == 3
