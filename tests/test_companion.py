import pygame
import settings
from entities import Player
from inventory import adopt_companion, upgrade_companion_ability, COMPANION_ABILITIES


def test_upgrade_companion_ability():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.money = 200
    player.energy = 100
    adopt_companion(player, 0)  # Dog
    msg = upgrade_companion_ability(player, 0)
    ability_name = COMPANION_ABILITIES[player.companion][0][0]
    assert ability_name in msg
    assert player.companion_abilities[player.companion][ability_name] == 1
