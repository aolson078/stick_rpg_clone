import pygame
import settings
from entities import Player
from cardgame import card_duel
from unittest.mock import patch


def test_card_duel_win_reward():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 50
    with patch('random.sample', side_effect=[["Slime", "Goblin", "Farmer"], ["Dragon", "Wizard", "Alien"]]):
        with patch('random.choice', return_value="Robot"):
            msg = card_duel(player)
    assert msg.startswith("You won")
    assert player.card_duels_won == 1
    assert "Robot" in player.cards
