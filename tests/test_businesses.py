import random
import pygame

from entities import Player
from businesses import (
    BUSINESS_CATALOG,
    BUSINESS_DATA,
    buy_business,
    upgrade_business,
    hire_staff,
    collect_profits,
)


def make_player():
    return Player(pygame.Rect(0, 0, 1, 1))


def test_buy_and_upgrade_business():
    p = make_player()
    p.money = 10000
    stall_index = BUSINESS_CATALOG.index("Stall")
    assert buy_business(p, stall_index) == "Bought Stall"
    assert "Stall" in p.businesses
    assert upgrade_business(p, "Stall") == "Upgraded Stall to Store"
    assert "Store" in p.businesses and "Stall" not in p.businesses


def test_staff_affects_profits():
    p = make_player()
    p.money = 10000
    store_index = BUSINESS_CATALOG.index("Store")
    buy_business(p, store_index)
    hire_staff(p, "Store", 2)
    p.charisma = 5

    orig_random = random.random
    random.random = lambda: 1.0  # avoid robbery
    try:
        profit = collect_profits(p)
    finally:
        random.random = orig_random

    data = BUSINESS_DATA["Store"]
    expected = data.base_profit + p.charisma * 2 + (2 * 10) - (2 * data.staff_cost)
    assert profit == expected


def test_robbery_zeroes_profit():
    p = make_player()
    p.money = 10000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)

    orig_random = random.random
    random.random = lambda: 0.0  # force robbery
    try:
        profit = collect_profits(p)
    finally:
        random.random = orig_random

    assert profit == 0

