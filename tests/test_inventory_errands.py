import pygame
import settings
import inventory
from entities import Player
from inventory import (
    COMPANION_ERRAND_FEE,
    schedule_companion_errand,
    resolve_companion_errands,
)


def make_player() -> Player:
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.money = 100
    player.energy = 100
    player.inventory.clear()
    return player


def test_schedule_requires_companion_and_morale():
    player = make_player()
    msg = schedule_companion_errand(player, 0)
    assert msg == "No companion available"

    player.companion = "Dog"
    player.companion_level = 1
    player.companion_morale = 20
    msg = schedule_companion_errand(player, 0)
    assert msg == "Companion morale too low"
    assert player.money == 100


def test_schedule_records_errand():
    player = make_player()
    player.companion = "Dog"
    player.companion_level = 1
    player.companion_morale = 80

    message = schedule_companion_errand(player, 0)
    assert "Dog" in message
    assert player.money == 100 - COMPANION_ERRAND_FEE
    assert len(player.companion_errands) == 1

    errand = player.companion_errands[0]
    assert errand["item_index"] == 0
    assert errand["penalty"]["money"] >= 5


def test_resolve_companion_errand_success(monkeypatch):
    player = make_player()
    player.companion = "Dog"
    player.companion_level = 1
    player.companion_morale = 80

    schedule_companion_errand(player, 0)
    monkeypatch.setattr(inventory.random, "random", lambda: 0.0)

    messages = resolve_companion_errands(player)
    assert any("fetched" in msg for msg in messages)
    assert any(item.name == "Cola" for item in player.inventory)
    assert not player.companion_errands
    assert player.companion_morale >= 80


def test_resolve_companion_errand_failure(monkeypatch):
    player = make_player()
    player.companion = "Dog"
    player.companion_level = 1
    player.companion_morale = 80

    schedule_companion_errand(player, 0)
    errand = player.companion_errands[0]
    money_after_fee = player.money
    morale_before = player.companion_morale
    rep_before = player.reputation.get("mayor", 0)

    monkeypatch.setattr(inventory.random, "random", lambda: 0.99)

    messages = resolve_companion_errands(player)
    assert any("failed" in msg for msg in messages)
    assert player.money == max(0, money_after_fee - errand["penalty"]["money"])
    assert player.companion_morale == max(0, morale_before - errand["penalty"]["morale"])
    assert player.reputation["mayor"] == rep_before - errand["penalty"]["reputation"][1]
    assert not player.inventory
    assert not player.companion_errands
