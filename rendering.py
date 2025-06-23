import math
import pygame
from settings import (
    PLAYER_HEAD_COLOR,
    PLAYER_COLOR,
    WINDOW_COLOR,
    DOOR_COLOR,
    BUILDING_COLOR,
    HOME_COLOR,
    JOB_COLOR,
    SHOP_COLOR,
    PARK_COLOR,
    GYM_COLOR,
    LIBRARY_COLOR,
    ROAD_COLOR,
    SIDEWALK_COLOR,
    CITY_WALL_COLOR,
    UI_BG,
    FONT_COLOR,
    MAP_WIDTH,
    MAP_HEIGHT,
    SCREEN_WIDTH,
)


def draw_player(surface, rect, frame=0):
    x = rect.x + rect.width // 2
    y = rect.y + rect.height
    shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 40, 80), (0, 0, 40, 14))
    surface.blit(shadow, (x - 20, y - 6))

    swing = math.sin(frame / 6) * 7 if frame else 0
    pygame.draw.circle(surface, PLAYER_HEAD_COLOR, (x, y - 24), 10)
    pygame.draw.circle(surface, PLAYER_COLOR, (x, y - 24), 10, 2)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y - 14), (x, y), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y - 10), (x - 13, y - 2 + int(swing)), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y - 10), (x + 13, y - 2 - int(swing)), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y), (x - 9, y + 16 + int(swing)), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y), (x + 9, y + 16 - int(swing)), 3)


def building_color(btype):
    if btype == "home":
        return HOME_COLOR
    if btype == "job":
        return JOB_COLOR
    if btype == "shop":
        return SHOP_COLOR
    if btype == "park":
        return PARK_COLOR
    if btype == "gym":
        return GYM_COLOR
    if btype == "library":
        return LIBRARY_COLOR
    return BUILDING_COLOR


def draw_building(surface, building):
    b = building.rect
    # Base rectangle
    pygame.draw.rect(surface, building_color(building.btype), b, border_radius=9)
    roof = pygame.Rect(b.x, b.y - 14, b.width, 18)
    pygame.draw.rect(surface, (150, 140, 100), roof, border_top_left_radius=9, border_top_right_radius=9)
    if building.btype != "park":
        for i in range(2, b.width // 50):
            wx = b.x + 18 + i * 50
            wy = b.y + 28
            pygame.draw.rect(surface, WINDOW_COLOR, (wx, wy, 22, 22), border_radius=4)
        dx = b.x + b.width // 2 - 18
        dy = b.y + b.height - 38
        pygame.draw.rect(surface, DOOR_COLOR, (dx, dy, 36, 38), border_radius=5)
        pygame.draw.circle(surface, (220, 210, 120), (dx + 32, dy + 19), 3)
    font = pygame.font.SysFont(None, 28)
    label = font.render(building.name, True, FONT_COLOR)
    label_bg = pygame.Surface((label.get_width() + 12, label.get_height() + 4), pygame.SRCALPHA)
    label_bg.fill((255, 255, 255, 230))
    surface.blit(label_bg, (b.x + b.width // 2 - label.get_width() // 2 - 6, b.y - 32))
    surface.blit(label, (b.x + b.width // 2 - label.get_width() // 2, b.y - 30))


def draw_road_and_sidewalks(surface, cam_x, cam_y):
    road_rect = pygame.Rect(0 - cam_x, 470 - cam_y, MAP_WIDTH, 60)
    pygame.draw.rect(surface, ROAD_COLOR, road_rect)
    pygame.draw.rect(surface, SIDEWALK_COLOR, (0 - cam_x, 460 - cam_y, MAP_WIDTH, 10))
    pygame.draw.rect(surface, SIDEWALK_COLOR, (0 - cam_x, 530 - cam_y, MAP_WIDTH, 10))
    for x in range(0, MAP_WIDTH, 80):
        pygame.draw.rect(surface, (230, 220, 100), (x - cam_x, 498 - cam_y, 36, 6), border_radius=3)


def draw_city_walls(surface, cam_x, cam_y):
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, MAP_WIDTH, 12))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, MAP_HEIGHT - 12 - cam_y, MAP_WIDTH, 12))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, 12, MAP_HEIGHT))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (MAP_WIDTH - 12 - cam_x, -cam_y, 12, MAP_HEIGHT))


def draw_day_night(surface, current_time):
    hour = (current_time / 60) % 24
    alpha = 0
    if 18 <= hour or hour < 6:
        if hour >= 18:
            alpha = min(int((hour - 18) / 6 * 120), 120)
        else:
            alpha = min(int((6 - hour) / 6 * 120), 120)
    if alpha:
        overlay = pygame.Surface((SCREEN_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))


def draw_ui(surface, font, player):
    bar = pygame.Surface((SCREEN_WIDTH, 36), pygame.SRCALPHA)
    bar.fill(UI_BG)
    hour = int(player.time) // 60
    minute = int(player.time) % 60
    time_str = f"{hour:02d}:{minute:02d}"
    text = font.render(
        f"Money: ${int(player.money)}  Energy: {int(player.energy)}  Health: {int(player.health)}  "
        f"STR: {player.strength}  INT: {player.intelligence}  CHA: {player.charisma}  "
        f"Day: {player.day}  Time: {time_str}",
        True,
        FONT_COLOR,
    )
    bar.blit(text, (16, 6))
    surface.blit(bar, (0, 0))
