import random
import pygame
import settings
from entities import Player
from inventory import buy_shop_item, get_shop_price, SHOP_ITEMS, dream_shop_purchase


def make_player():
    return Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))


def test_shop_price_base():
    player = make_player()
    base = SHOP_ITEMS[0]["cost"]
    assert get_shop_price(player, 0) == base


def test_shop_price_fluctuates():
    player = make_player()
    player.day = 2
    player.season = "Winter"
    r = random.Random(player.day).random()
    expected = int(round(SHOP_ITEMS[0]["cost"] * 1.2 * (0.8 + r * 0.4)))
    assert get_shop_price(player, 0) == expected


def find_shop_index(name: str) -> int:
    for i, item in enumerate(SHOP_ITEMS):
        if item["name"] == name:
            return i
    raise ValueError(name)


def test_buy_shop_item_with_cards_success():
    player = make_player()
    idx = find_shop_index("Leather Helmet")
    player.money = 0
    player.cards = ["Slime", "Slime", "Goblin", "Goblin"]

    message = buy_shop_item(player, idx, payment="card")

    assert message.startswith("Traded cards for Leather Helmet")
    assert player.cards.count("Slime") == 1
    assert player.cards.count("Goblin") == 1
    assert player.money == 0
    assert player.inventory[-1].name == "Leather Helmet"


def test_buy_shop_item_with_cards_requires_duplicates():
    player = make_player()
    idx = find_shop_index("Magic Wand")
    player.money = 0
    original_cards = ["Phoenix", "Slime", "Slime", "Goblin", "Goblin"]
    player.cards = list(original_cards)

    message = buy_shop_item(player, idx, payment="card")

    assert message == "Need more duplicate cards"
    assert player.cards == original_cards


def test_buy_shop_item_cash_still_works():
    player = make_player()
    idx = find_shop_index("Leather Armor")
    price = get_shop_price(player, idx)
    player.money = price + 10

    message = buy_shop_item(player, idx)

    assert message == "Bought Leather Armor"
    assert player.money == 10
    assert player.inventory[-1].name == "Leather Armor"


def test_dream_shop_purchase_applies_effect_and_deducts_shards():
    player = make_player()
    player.dream_shards = 10
    offers = [
        {"name": "Focus Draught", "cost": 4, "effect": {"type": "stat", "stat": "intelligence", "amount": 2}},
        {"name": "Charm Sigil", "cost": 3, "effect": "lucid_charm"},
    ]

    message = dream_shop_purchase(player, offers, 0)
    assert message == "Bought Focus Draught"
    assert player.dream_shards == 6
    assert player.intelligence == 3
    assert offers[0]["purchased"] is True

    message = dream_shop_purchase(player, offers, 1)
    assert message == "Bought Charm Sigil"
    assert player.dream_shards == 3
    assert player.charisma == 2
    assert offers[1]["purchased"] is True


def test_dream_shop_purchase_requires_shards_and_prevents_repeat():
    player = make_player()
    player.dream_shards = 3
    offers = [{"name": "Token Fragment", "cost": 4, "effect": "lucid_token"}]

    message = dream_shop_purchase(player, offers, 0)
    assert message == "Not enough dream shards"
    assert player.dream_shards == 3
    assert "purchased" not in offers[0]

    player.dream_shards = 5
    message = dream_shop_purchase(player, offers, 0)
    assert message == "Bought Token Fragment"
    assert player.dream_shards == 1
    assert offers[0]["purchased"] is True

    message = dream_shop_purchase(player, offers, 0)
    assert message == "Sold out"
    assert player.dream_shards == 1
