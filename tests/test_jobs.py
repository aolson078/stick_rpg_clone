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


def test_work_job_temporary_bonuses():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 100
    player.money = 0
    player.temporary_bonuses["fortune"] = {"value": 2, "expires": player.day}
    player.temporary_bonuses["clarity"] = {"value": 1, "expires": player.day}

    result = work_job(player, "office")

    assert result == "Worked as Intern! +$30, +15xp"
    assert player.money == 30
    assert player.office_exp == 15
    assert player.energy == 80

