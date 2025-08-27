import pygame
import settings
from entities import Player, InventoryItem
import helpers


def test_save_and_load_game(tmp_path):
    save_file = tmp_path / "savegame.json"
    old_path = helpers.SAVE_FILE
    helpers.SAVE_FILE = str(save_file)
    try:
        player = Player(pygame.Rect(0, 0, settings.PLAYER_SIZE, settings.PLAYER_SIZE))
        player.name = "TestPlayer"
        player.money = 123
        player.pants_color = (1, 2, 3)
        player.has_hat = True
        player.hat_color = (4, 5, 6)
        player.inventory.append(InventoryItem("Test Item", "weapon", attack=2))

        helpers.save_game(player)
        assert save_file.exists()

        loaded = helpers.load_game()
        assert loaded is not None
        assert loaded.name == player.name
        assert loaded.money == player.money
        assert loaded.pants_color == player.pants_color
        assert loaded.has_hat == player.has_hat
        assert loaded.hat_color == player.hat_color
        assert any(item.name == "Test Item" for item in loaded.inventory)
    finally:
        helpers.SAVE_FILE = old_path

