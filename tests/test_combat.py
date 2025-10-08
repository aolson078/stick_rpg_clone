import pygame
import settings
from entities import Player
from combat import fight_brawler, fight_enemy, BRAWLER_COUNT, energy_cost, _combat_stats
from entities import InventoryItem


def test_fight_brawler_too_tired():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.energy = 5
    result = fight_brawler(player)
    assert result == "Too tired to fight!"


def test_fight_brawler_no_challengers():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.brawls_won = BRAWLER_COUNT
    result = fight_brawler(player)
    assert result == "No challengers remain"


def test_special_ability_resets_after_fight():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    player.strength = 10
    player.energy = 50
    weapon = InventoryItem("Test Sword", "weapon", attack=5)
    player.equipment["weapon"] = weapon
    player.active_ability = "special"
    fight_enemy(player)
    assert player.active_ability is None


def test_energy_cost_reduced_by_fortitude_bonus():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    baseline = energy_cost(player, 20)
    player.temporary_bonuses["fortitude"] = {"value": 1, "expires": player.day}
    reduced = energy_cost(player, 20)

    assert baseline == 20
    assert reduced < baseline


def test_combat_stats_gain_defense_from_fortitude_bonus():
    player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
    base_df = player.defense
    player.temporary_bonuses["fortitude"] = {"value": 2, "expires": player.day}

    _, df, _, _ = _combat_stats(player)

    assert df == base_df + 2

