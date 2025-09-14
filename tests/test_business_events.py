import random
import pygame
from businesses import BUSINESS_CATALOG, buy_business, collect_profits
from entities import Player


def make_player():
    return Player(pygame.Rect(0, 0, 1, 1))


def test_random_event_positive():
    p = make_player()
    p.money = 1000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)
    # avoid robbery then trigger boom
    orig_random = random.random
    seq = iter([1.0, 0.15])
    random.random = lambda: next(seq)
    try:
        profit, events = collect_profits(p)
    finally:
        random.random = orig_random
    assert profit == 25 + 2 + 50  # base + charisma + boom bonus
    assert any("boom" in msg.lower() for msg in events)
    assert p.reputation["business"] > 0


def test_random_event_negative():
    p = make_player()
    p.money = 1000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)
    orig_random = random.random
    seq = iter([1.0, 0.05])  # avoid robbery then inspection
    random.random = lambda: next(seq)
    try:
        profit, events = collect_profits(p)
    finally:
        random.random = orig_random
    assert profit == 25 + 2 - 20  # base + charisma - inspection fine
    assert any("inspection" in msg.lower() for msg in events)
    assert p.reputation["business"] < 0
