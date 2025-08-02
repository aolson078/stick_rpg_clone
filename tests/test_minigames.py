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
    with patch('random.random', side_effect=[0.6, 0.6]):
        with patch('random.randint', return_value=30):
            msg = go_fishing(player, difficulty='hard')
    assert msg.startswith("Caught a fish")
    assert player.money >= 30
    assert "Master Angler" in player.achievements
    assert "Fishing Legend" in player.cards
