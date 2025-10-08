import pygame
import settings
import quests
from entities import Player
from helpers import advance_day
from quests import random_event


def test_fortune_bonus_softens_negative_event(monkeypatch):
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.money = 100
    player.temporary_bonuses["fortune"] = {"value": 1, "expires": player.day}
    player.time = 12 * 60

    thief_event = next(
        ev for ev in quests.EVENTS if ev.description == "A thief stole $10 from you!"
    )
    monkeypatch.setattr(quests.random, "random", lambda: 0.0)
    monkeypatch.setattr(quests.random, "choices", lambda pool, weights, k: [thief_event])

    message = random_event(player)

    assert message is not None
    assert "Fortune softens the blow" in message
    assert player.money == 95


def test_advance_day_clears_expired_bonuses():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.temporary_bonuses["clarity"] = {"value": 1, "expires": player.day}

    advance_day(player)
    assert "clarity" not in player.temporary_bonuses
