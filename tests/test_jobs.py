import pygame
import settings
from entities import Player
from careers import work_job


def test_work_job_basic():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 100
    result = work_job(player, "office")
    assert result == "Worked as Intern! +$20, +10xp"
    assert player.energy == 80
    assert player.money == 70
    assert player.office_shifts == 1
    assert player.office_exp == 10


def test_work_job_promotion():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.intelligence = 5
    player.charisma = 5
    player.office_exp = 90
    result = work_job(player, "office")
    assert result == "Promoted to Clerk!"
    assert player.office_level == 2
    assert player.office_shifts == 0
    assert player.office_exp == 0
    assert player.intelligence == 6

