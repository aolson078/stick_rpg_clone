import math
import os
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
    CLINIC_COLOR,
    BAR_COLOR,
    ROAD_COLOR,
    SIDEWALK_COLOR,
    CITY_WALL_COLOR,
    UI_BG,
    FONT_COLOR,
    MAP_WIDTH,
    MAP_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

PERK_MAX_LEVEL = 3
PLAYER_SPRITES = []


def load_player_sprites():
    """Load player sprite frames from the assets folder."""
    global PLAYER_SPRITES
    if PLAYER_SPRITES:
        return PLAYER_SPRITES
    for i in range(3):
        path = os.path.join("assets", f"player_{i}.png")
        if os.path.exists(path):
            PLAYER_SPRITES.append(pygame.image.load(path).convert_alpha())
    return PLAYER_SPRITES


def draw_player_sprite(surface, rect, frame=0):
    sprites = load_player_sprites()
    if not sprites:
        return draw_player(surface, rect, frame)
    image = sprites[frame % len(sprites)]
    x = rect.x + rect.width // 2 - image.get_width() // 2
    y = rect.y + rect.height - image.get_height()
    shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 40, 80), (0, 0, 40, 14))
    surface.blit(shadow, (x + image.get_width() // 2 - 20, y + image.get_height() - 6))
    surface.blit(image, (x, y))


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
    if btype == "clinic":
        return CLINIC_COLOR
    if btype == "bar":
        return BAR_COLOR
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



def draw_ui(surface, font, player, quests):

    bar = pygame.Surface((SCREEN_WIDTH, 36), pygame.SRCALPHA)
    bar.fill(UI_BG)
    hour = int(player.time) // 60
    minute = int(player.time) % 60
    time_str = f"{hour:02d}:{minute:02d}"
    text = font.render(
        f"Money: ${int(player.money)}  Tokens: {player.tokens}  Energy: {int(player.energy)}  Health: {int(player.health)}  "
        f"STR:{player.strength} DEF:{player.defense} SPD:{player.speed} INT:{player.intelligence} CHA:{player.charisma}  "

        f"Office Lv: {player.office_level}  Dealer Lv: {player.dealer_level}  Clinic Lv: {player.clinic_level}  Day: {player.day}  Time: {time_str}",
        True,
        FONT_COLOR,
    )
    bar.blit(text, (16, 6))
    if player.companion:
        ctxt = font.render(f"Pet: {player.companion}", True, FONT_COLOR)
        bar.blit(ctxt, (SCREEN_WIDTH - ctxt.get_width() - 20, 6))
    surface.blit(bar, (0, 0))

    # Show current quest below the stat bar
    quest_text = None
    if player.current_quest < len(quests):
        quest_text = quests[player.current_quest].description
    if quest_text:
        qsurf = font.render(f"Quest: {quest_text}", True, FONT_COLOR)
        qbg = pygame.Surface((qsurf.get_width() + 12, qsurf.get_height() + 4), pygame.SRCALPHA)
        qbg.fill((255, 255, 255, 220))
        surface.blit(qbg, (16, 40))
        surface.blit(qsurf, (22, 42))


def draw_inventory_screen(surface, font, player, slot_rects, item_rects, dragging):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Inventory", True, FONT_COLOR)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    for slot, rect in slot_rects.items():
        pygame.draw.rect(surface, (210, 210, 210), rect)
        label = font.render(slot.title(), True, FONT_COLOR)
        surface.blit(label, (rect.x + 2, rect.y - 20))
        item = player.equipment.get(slot)
        if item:
            it = font.render(
                f"{item.name} A{item.attack} D{item.defense} S{item.speed}", True, FONT_COLOR
            )
            surface.blit(it, (rect.x + 4, rect.y + 20))

    for rect, item in item_rects:
        pygame.draw.rect(surface, (200, 220, 230), rect)
        txt = font.render(
            f"{item.name} A{item.attack} D{item.defense} S{item.speed}", True, FONT_COLOR
        )
        surface.blit(txt, (rect.x + 4, rect.y + 20))

    if dragging:
        item, pos = dragging
        txt = font.render(
            f"{item.name} A{item.attack} D{item.defense} S{item.speed}", True, FONT_COLOR
        )
        bg = pygame.Surface((60, 60), pygame.SRCALPHA)
        bg.fill((230, 230, 240, 200))
        bg_rect = bg.get_rect(center=pos)
        surface.blit(bg, bg_rect.topleft)
        surface.blit(txt, (bg_rect.x + 4, bg_rect.y + 20))


def draw_perk_menu(surface, font, player, perks):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Choose a Perk", True, FONT_COLOR)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    for i, (name, desc) in enumerate(perks):
        level = player.perk_levels.get(name, 0)
        txt = font.render(
            f"{i+1}: {name} Lv{level}/{PERK_MAX_LEVEL} - {desc}", True, FONT_COLOR
        )
        surface.blit(txt, (100, 120 + i * 40))

    info = font.render(f"Points: {player.perk_points}   [Q] Exit", True, FONT_COLOR)
    surface.blit(info, (100, 120 + len(perks) * 40 + 20))


def draw_quest_log(surface, font, quests):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Quest Log", True, FONT_COLOR)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    for i, q in enumerate(quests):
        status = "[x]" if q.completed else "[ ]"
        txt = font.render(f"{status} {q.description}", True, FONT_COLOR)
        surface.blit(txt, (100, 120 + i * 30))

    note = font.render("Press L or Q to close", True, FONT_COLOR)
    surface.blit(note, (100, SCREEN_HEIGHT - 140))


def draw_home_interior(surface, font, player, frame, bed_rect, door_rect):
    """Draw a simple interior of the player's home."""
    surface.fill((235, 225, 200))
    # walls
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, SCREEN_WIDTH, 40))
    pygame.draw.rect(surface, (160, 140, 110), (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, 40, SCREEN_HEIGHT))
    pygame.draw.rect(surface, (160, 140, 110), (SCREEN_WIDTH - 40, 0, 40, SCREEN_HEIGHT))

    # bed
    pygame.draw.rect(surface, (200, 70, 70), bed_rect)
    pygame.draw.rect(surface, (255, 255, 255), bed_rect.inflate(-20, -20))

    # door
    pygame.draw.rect(surface, (100, 80, 60), door_rect)
    pygame.draw.circle(surface, (220, 210, 120), (door_rect.right - 20, door_rect.centery), 6)

    draw_player_sprite(surface, player.rect, frame)
    if player.companion:
        pos = (bed_rect.x + bed_rect.width + 60, bed_rect.y + bed_rect.height - 30)
        color = (150, 120, 80)
        if player.companion == "Cat":
            color = (170, 170, 220)
        elif player.companion == "Parrot":
            color = (200, 200, 60)
        pygame.draw.circle(surface, color, pos, 20)


def draw_bar_interior(
    surface,
    font,
    player,
    frame,
    counter_rect,
    bj_rect,
    slot_rect,
    brawl_rect,
    door_rect,
):
    """Draw the interior of the bar with simple interaction spots."""
    surface.fill((225, 205, 170))

    pygame.draw.rect(surface, (160, 140, 110), (0, 0, SCREEN_WIDTH, 40))
    pygame.draw.rect(surface, (160, 140, 110), (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, 40, SCREEN_HEIGHT))
    pygame.draw.rect(surface, (160, 140, 110), (SCREEN_WIDTH - 40, 0, 40, SCREEN_HEIGHT))

    # counter for buying tokens
    pygame.draw.rect(surface, (120, 80, 60), counter_rect)
    pygame.draw.rect(surface, (180, 140, 100), counter_rect.inflate(-20, -20))
    ct = font.render("Tokens", True, FONT_COLOR)
    surface.blit(ct, (counter_rect.x + 20, counter_rect.y + counter_rect.height // 2 - 10))

    # blackjack table
    pygame.draw.rect(surface, (60, 120, 60), bj_rect)
    bj = font.render("Blackjack", True, (250, 250, 250))
    surface.blit(bj, (bj_rect.x + 20, bj_rect.y + bj_rect.height // 2 - 10))

    # slots
    pygame.draw.rect(surface, (90, 90, 150), slot_rect)
    sl = font.render("Slots", True, (250, 250, 250))
    surface.blit(sl, (slot_rect.x + 20, slot_rect.y + slot_rect.height // 2 - 10))

    # fighting ring
    pygame.draw.rect(surface, (180, 70, 70), brawl_rect)
    fb = font.render("Fight", True, (250, 250, 250))
    surface.blit(fb, (brawl_rect.x + 20, brawl_rect.y + brawl_rect.height // 2 - 10))

    pygame.draw.rect(surface, (100, 80, 60), door_rect)
    pygame.draw.circle(surface, (220, 210, 120), (door_rect.right - 20, door_rect.centery), 6)

    draw_player_sprite(surface, player.rect, frame)

