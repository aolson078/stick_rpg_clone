import pygame
from entities import Player
from inventory import adopt_companion, feed_animals, train_companion


def test_companion_morale_adjustments():
    player = Player(pygame.Rect(0, 0, 10, 10))
    player.money = 1000
    adopt_companion(player, 0)  # Dog
    assert player.companion_morale == 100

    player.animals["chicken"] = 1
    player.companion_morale = 90
    feed_animals(player, "chicken")
    assert player.companion_morale == 95

    player.companion_morale = 15
    train_companion(player)
    assert player.companion_morale == 5
