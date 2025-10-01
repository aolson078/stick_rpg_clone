import pygame
import settings
from entities import Player
from helpers import play_darts, go_fishing, play_blackjack
from unittest.mock import patch


def make_player():
    return Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))


def test_darts_hard_grants_card():
    player = make_player()
    player.tokens = 1
    player.speed = 4
    with patch('random.randint', return_value=20):
        msg = play_darts(player, difficulty='hard')
    assert "Bullseye" in msg
    assert player.tokens == 3
    assert "Darts Champion" in player.achievements
    assert "Dart Master" in player.cards


def test_blackjack_perfect_score_unlocks_rewards():
    player = make_player()
    player.tokens = 1
    with patch('random.randint', side_effect=[21, 18]):
        msg = play_blackjack(player, difficulty='hard')
    assert "You win" in msg
    assert player.tokens == 3
    assert "Blackjack Champion" in player.achievements
    assert "Blackjack Shark" in player.cards


def test_fishing_hard_big_catch_rewards():
    player = make_player()
    player.energy = 50
    player.fishing_skill = 3
    king_salmon = {
        "name": "King Salmon",
        "rarity": 0.3,
        "money_range": (30, 30),
        "xp": 26,
        "weight_divisor": 2.5,
        "requires_level": 3,
    }
    with patch('random.random', side_effect=[0.6, 0.6]):
        with patch('helpers._choose_fishing_result', return_value=king_salmon):
            msg = go_fishing(player, difficulty='hard')
    assert msg.startswith("Caught a King Salmon")
    assert player.money >= 30
    assert "Master Angler" in player.achievements
    assert "Fishing Legend" in player.cards
    assert player.fishing_log["King Salmon"]["count"] == 1


def test_fishing_levels_up_and_logs_records():
    player = make_player()
    player.energy = 50
    trout = {
        "name": "River Trout",
        "rarity": 0.45,
        "money_range": (15, 15),
        "xp": 50,
        "weight_divisor": 4,
    }
    with patch('random.random', side_effect=[0.6, 0.6]):
        with patch('helpers._choose_fishing_result', return_value=trout):
            msg = go_fishing(player, difficulty='normal')
    assert player.fishing_skill == 2
    assert player.fishing_exp == 10
    assert "Fishing level up" in msg
    log = player.fishing_log["River Trout"]
    assert log["count"] == 1
    assert log["best_reward"] >= 15
