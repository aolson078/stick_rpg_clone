"""Rendering helper functions for sprites, UI, and locations."""
import math
import os
import random
import pygame
import settings
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
    BUS_STOP_COLOR,
    CITY_WALL_COLOR,
    UI_BG,
    FONT_COLOR,
    MAP_WIDTH,
    MAP_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_COLOR,
    TREE_COLOR,
    TRUNK_COLOR,
    FLOWER_COLORS,
    SHADOW_COLOR,
)
from tilemap import TileMap
from careers import get_job_title, job_progress
from inventory import crafting_exp_needed, CROPS
from constants import PERK_MAX_LEVEL
from helpers import scaled_font
from quests import SIDE_QUESTS, COMPANION_QUESTS
import factions

PLAYER_SPRITES = []
PLAYER_SPRITE_COLOR = None
FOREST_ENEMY_IMAGES = []
STARS = []
CLOUDS = []
RAINDROPS = []
SNOWFLAKES = []
CITY_MAP = None


def load_player_sprites(color=None):
    """Load player sprite frames and optionally tint them."""
    global PLAYER_SPRITES, PLAYER_SPRITE_COLOR
    if PLAYER_SPRITES and PLAYER_SPRITE_COLOR == color:
        return PLAYER_SPRITES

    def tint(img, col):
        tinted = img.copy()
        overlay = pygame.Surface(img.get_size()).convert_alpha()
        overlay.fill(col)
        tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted

    PLAYER_SPRITES = []
    PLAYER_SPRITE_COLOR = color
    i = 0
    while True:
        path = os.path.join(settings.IMAGE_DIR, f"player_{i}.png")
        if not os.path.exists(path):
            break
        img = pygame.image.load(path).convert_alpha()
        if color:
            img = tint(img, color)
        PLAYER_SPRITES.append(img)
        i += 1
    return PLAYER_SPRITES


def draw_player_sprite(
    surface, rect, frame=0, facing_left=False, color=None, head_color=None
):
    sprites = load_player_sprites(color)
    if not sprites:
        return draw_player(surface, rect, frame, facing_left, color, head_color)
    image = sprites[frame % len(sprites)]
    if facing_left:
        image = pygame.transform.flip(image, True, False)
    x = rect.x + rect.width // 2 - image.get_width() // 2
    y = rect.y + rect.height - image.get_height()
    shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 40, 80), (0, 0, 40, 14))
    surface.blit(shadow, (x + image.get_width() // 2 - 20, y + image.get_height() - 6))

    surface.blit(image, (x, y))


def draw_player(surface, rect, frame=0, facing_left=False, color=None, head_color=None):
    """Fallback stick figure drawing if sprites fail to load."""
    x = rect.x + rect.width // 2
    y = rect.y + rect.height
    shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 40, 80), (0, 0, 40, 14))
    surface.blit(shadow, (x - 20, y - 6))

    swing = math.sin(frame / 6) * 7 if frame else 0
    color = color or PLAYER_COLOR
    head_color = head_color or PLAYER_HEAD_COLOR
    pygame.draw.circle(surface, head_color, (x, y - 24), 10)
    pygame.draw.circle(surface, color, (x, y - 24), 10, 2)
    pygame.draw.line(surface, color, (x, y - 14), (x, y), 3)
    arm_offset = -13 if not facing_left else 13
    leg_offset = -9 if not facing_left else 9
    pygame.draw.line(
        surface, color, (x, y - 10), (x + arm_offset, y - 2 + int(swing)), 3
    )
    pygame.draw.line(
        surface, color, (x, y - 10), (x - arm_offset, y - 2 - int(swing)), 3
    )
    pygame.draw.line(surface, color, (x, y), (x + leg_offset, y + 16 + int(swing)), 3)
    pygame.draw.line(surface, color, (x, y), (x - leg_offset, y + 16 - int(swing)), 3)


def draw_npc(surface, npc, font, offset=(0, 0)):
    """Draw an NPC with optional speech bubble."""
    rect = npc.rect.move(offset)
    pygame.draw.rect(surface, (60, 120, 220), rect)
    if npc.bubble_timer > 0 and npc.bubble_message:
        msg_surf = font.render(npc.bubble_message, True, (30, 30, 30))
        bg = pygame.Surface(
            (msg_surf.get_width() + 10, msg_surf.get_height() + 6), pygame.SRCALPHA
        )
        bg.fill((255, 255, 255, 230))
        bx = rect.centerx - bg.get_width() // 2
        by = rect.top - bg.get_height() - 8
        surface.blit(bg, (bx, by))
        surface.blit(msg_surf, (bx + 5, by + 3))


def draw_quest_marker(surface, player_rect, target_rect, cam_x, cam_y):
    """Draw an arrow above the player pointing toward the target."""
    px = player_rect.centerx - cam_x
    py = player_rect.centery - cam_y
    tx = target_rect.centerx - cam_x
    ty = target_rect.centery - cam_y
    angle = math.atan2(ty - py, tx - px)
    x = px
    y = py - 40
    tip = (x + 20 * math.cos(angle), y + 20 * math.sin(angle))
    left = (
        x + 8 * math.cos(angle + math.pi * 0.75),
        y + 8 * math.sin(angle + math.pi * 0.75),
    )
    right = (
        x + 8 * math.cos(angle - math.pi * 0.75),
        y + 8 * math.sin(angle - math.pi * 0.75),
    )
    pygame.draw.polygon(surface, (255, 50, 50), [tip, left, right])


def building_color(btype):
    """Return the color used to draw a building type."""
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
    if btype == "bus_stop":
        return BUS_STOP_COLOR
    if btype == "bank":
        return BAR_COLOR
    if btype == "farm":
        return PARK_COLOR
    if btype == "mall":
        return SHOP_COLOR
    if btype == "beach":
        return PARK_COLOR
    if btype == "suburbs":
        return HOME_COLOR
    return BUILDING_COLOR


def draw_building(surface, building, highlight=False):
    """Draw a city building, optionally highlighted."""
    b = building.rect
    if building.image:
        shadow = pygame.Surface((b.width, b.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, SHADOW_COLOR, shadow.get_rect(), border_radius=9)
        surface.blit(shadow, (b.x + 4, b.y + 4))
        sprite = pygame.transform.smoothscale(building.image, (b.width, b.height))
        surface.blit(sprite, (b.x, b.y))
        if highlight:
            pygame.draw.rect(surface, (255, 255, 0), b, 2, border_radius=9)
    else:
        color = building_color(building.btype)
        if highlight:
            color = tuple(min(255, c + 40) for c in color)
        shadow = pygame.Surface((b.width, b.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, SHADOW_COLOR, shadow.get_rect(), border_radius=9)
        surface.blit(shadow, (b.x + 4, b.y + 4))
        # base rectangle for the building
        pygame.draw.rect(surface, color, b, border_radius=9)

        # subtle vertical gradient to give the building more depth
        grad = pygame.Surface((b.width, b.height), pygame.SRCALPHA)
        for y in range(b.height):
            alpha = int(90 * (y / b.height))
            pygame.draw.line(grad, (0, 0, 0, alpha), (0, y), (b.width, y))
        mask = pygame.Surface((b.width, b.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=9)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad, (b.x, b.y))

        if highlight:
            pygame.draw.rect(surface, (255, 255, 0), b, 2, border_radius=9)
        roof = pygame.Rect(b.x, b.y - 14, b.width, 18)
        pygame.draw.rect(
            surface,
            (150, 140, 100),
            roof,
            border_top_left_radius=9,
            border_top_right_radius=9,
        )
        if building.btype != "park":
            for i in range(2, b.width // 50):
                wx = b.x + 18 + i * 50
                wy = b.y + 28
                pygame.draw.rect(surface, WINDOW_COLOR, (wx, wy, 22, 22), border_radius=4)
            dx = b.x + b.width // 2 - 18
            dy = b.y + b.height - 38
            pygame.draw.rect(surface, DOOR_COLOR, (dx, dy, 36, 38), border_radius=5)
            pygame.draw.circle(surface, (220, 210, 120), (dx + 32, dy + 19), 3)
    font = scaled_font(28)
    label = font.render(building.name, True, FONT_COLOR)
    label_bg = pygame.Surface(
        (label.get_width() + 12, label.get_height() + 4), pygame.SRCALPHA
    )
    label_bg.fill((255, 255, 255, 230))
    surface.blit(label_bg, (b.x + b.width // 2 - label.get_width() // 2 - 6, b.y - 32))
    surface.blit(label, (b.x + b.width // 2 - label.get_width() // 2, b.y - 30))


def draw_minimap(surface, player_rect, buildings, npcs=None, target=None, scale=0.1):
    """Render a simple minimap showing buildings, NPCs and the player."""
    width = int(MAP_WIDTH * scale)
    height = int(MAP_HEIGHT * scale)
    minimap = pygame.Surface((width, height), pygame.SRCALPHA)
    minimap.fill(UI_BG)
    minimap.set_alpha(200)

    # draw buildings
    for b in buildings:
        rect = pygame.Rect(
            int(b.rect.x * scale),
            int(b.rect.y * scale),
            max(2, int(b.rect.width * scale)),
            max(2, int(b.rect.height * scale)),
        )
        pygame.draw.rect(minimap, building_color(b.btype), rect)

    # quest target highlight
    if target:
        rect = pygame.Rect(
            int(target.rect.x * scale),
            int(target.rect.y * scale),
            max(2, int(target.rect.width * scale)),
            max(2, int(target.rect.height * scale)),
        )
        pygame.draw.rect(minimap, (255, 0, 0), rect, 2)

    # draw NPCs
    if npcs:
        for n in npcs:
            x = int(n.rect.centerx * scale)
            y = int(n.rect.centery * scale)
            pygame.draw.circle(minimap, (0, 0, 255), (x, y), 3)

    # draw player
    px = int(player_rect.centerx * scale)
    py = int(player_rect.centery * scale)
    pygame.draw.circle(minimap, (255, 255, 255), (px, py), 4)

    pygame.draw.rect(minimap, (255, 255, 255), minimap.get_rect(), 1)
    surface.blit(minimap, (SCREEN_WIDTH - width - 10, 10))


def draw_road_and_sidewalks(surface, cam_x, cam_y):
    """Render the city ground using a tile map."""
    global CITY_MAP
    if CITY_MAP is None:
        map_path = os.path.join(settings.IMAGE_DIR, "tiles", "city.tmx")
        CITY_MAP = TileMap(map_path)
    CITY_MAP.render(surface, cam_x, cam_y)


def draw_city_walls(surface, cam_x, cam_y):
    """Draw the outer walls surrounding the city map."""
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, MAP_WIDTH, 12))
    pygame.draw.rect(
        surface, CITY_WALL_COLOR, (-cam_x, MAP_HEIGHT - 12 - cam_y, MAP_WIDTH, 12)
    )
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, 12, MAP_HEIGHT))
    pygame.draw.rect(
        surface, CITY_WALL_COLOR, (MAP_WIDTH - 12 - cam_x, -cam_y, 12, MAP_HEIGHT)
    )


def _draw_tree(surface, x, y):
    "Draw a simple tree with layered foliage for a fuller look."
    pygame.draw.rect(surface, TRUNK_COLOR, (x + 10, y + 24, 12, 20))
    base = (x + 16, y + 16)
    pygame.draw.circle(surface, TREE_COLOR, base, 20)
    light = tuple(min(255, c + 40) for c in TREE_COLOR)
    dark = tuple(max(0, c - 40) for c in TREE_COLOR)
    pygame.draw.circle(surface, light, (x + 10, y + 12), 16)
    pygame.draw.circle(surface, dark, (x + 22, y + 14), 16)


def _draw_flower_patch(surface, x, y):
    "Draw a small patch of flowers."
    for i, color in enumerate(FLOWER_COLORS):
        ox = (i % 2) * 6
        oy = (i // 2) * 6
        pygame.draw.circle(surface, color, (x + ox, y + oy), 3)
        pygame.draw.circle(surface, (255, 255, 255), (x + ox, y + oy), 1)


def draw_decorations(surface, cam_x, cam_y):
    "Render decorative trees and flowers on the map."
    for x in range(100, MAP_WIDTH, 300):
        _draw_tree(surface, x - cam_x, 100 - cam_y)
    patches = [(500, 620), (900, 620), (2000, 620), (2500, 900)]
    for fx, fy in patches:
        _draw_flower_patch(surface, fx - cam_x, fy - cam_y)


def draw_sky(surface, current_time):
    """Draw a vertical gradient sky background with a sun or moon."""
    top_color = (120, 180, 255)
    bottom_color = BG_COLOR
    for y in range(settings.SCREEN_HEIGHT):
        ratio = y / settings.SCREEN_HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (settings.SCREEN_WIDTH, y))

    # stars remain fixed across frames
    if not STARS:
        for _ in range(80):
            sx = random.randint(0, settings.SCREEN_WIDTH - 1)
            sy = random.randint(0, settings.SCREEN_HEIGHT // 2)
            STARS.append((sx, sy))

    # generate a few cloud sprites on first call
    if not CLOUDS:
        for _ in range(6):
            w = random.randint(120, 220)
            h = random.randint(40, 80)
            cloud = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud, (255, 255, 255, 230), (0, h // 3, w, h // 2))
            pygame.draw.ellipse(cloud, (255, 255, 255, 230), (w // 4, 0, w // 2, h))
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(40, 200)
            speed = random.uniform(0.2, 0.7)
            CLOUDS.append([cloud, x, y, speed])

    # move and draw clouds
    for cloud in CLOUDS:
        cloud[1] -= cloud[3]
        if cloud[1] < -cloud[0].get_width():
            cloud[1] = settings.SCREEN_WIDTH + random.randint(20, 100)
            cloud[2] = random.randint(40, 200)
            cloud[3] = random.uniform(0.2, 0.7)
        surface.blit(cloud[0], (cloud[1], cloud[2]))

    # add a simple sun or moon that moves across the sky
    day_fraction = (current_time % (24 * 60)) / (24 * 60)
    x = int(day_fraction * settings.SCREEN_WIDTH)
    y = int(80 - 60 * math.cos(day_fraction * 2 * math.pi))
    hour = int(current_time) // 60
    if 6 <= hour < 18:
        pygame.draw.circle(surface, (255, 240, 150), (x, y), 40)
    else:
        pygame.draw.circle(surface, (230, 230, 255), (x, y), 30)
        for sx, sy in STARS:
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 2)


def draw_day_night(surface, current_time):
    """Darken the city during nighttime hours."""
    hour = int(current_time) // 60
    alpha = 0
    if hour >= 18 or hour < 6:
        if hour >= 18:
            alpha = min(int((hour - 18) / 6 * 120), 120)
        else:
            alpha = min(int((6 - hour) / 6 * 120), 120)
    if alpha:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))


def draw_weather(surface, weather):
    """Render simple rain or snow particle effects."""
    global RAINDROPS, SNOWFLAKES
    if weather == "Rain":
        if not RAINDROPS:
            RAINDROPS = [
                [
                    random.randint(0, settings.SCREEN_WIDTH),
                    random.randint(-settings.SCREEN_HEIGHT, 0),
                ]
                for _ in range(180)
            ]
        for drop in RAINDROPS:
            drop[0] += -3
            drop[1] += 15
            if drop[1] > settings.SCREEN_HEIGHT:
                drop[0] = random.randint(0, settings.SCREEN_WIDTH)
                drop[1] = random.randint(-40, 0)
            pygame.draw.line(
                surface,
                (180, 180, 255),
                (drop[0], drop[1]),
                (drop[0] + 3, drop[1] + 8),
                1,
            )
        SNOWFLAKES = []
    elif weather == "Snow":
        if not SNOWFLAKES:
            SNOWFLAKES = [
                [
                    random.randint(0, settings.SCREEN_WIDTH),
                    random.randint(-settings.SCREEN_HEIGHT, 0),
                    random.randint(1, 3),
                ]
                for _ in range(120)
            ]
        for flake in SNOWFLAKES:
            flake[0] += math.sin(flake[1] * 0.05) * flake[2]
            flake[1] += flake[2]
            if flake[1] > settings.SCREEN_HEIGHT:
                flake[0] = random.randint(0, settings.SCREEN_WIDTH)
                flake[1] = random.randint(-40, 0)
            pygame.draw.circle(
                surface, (255, 255, 255), (int(flake[0]), int(flake[1])), 2
            )
        RAINDROPS = []
    else:
        RAINDROPS = []
        SNOWFLAKES = []


def draw_ui(surface, font, player, quests, story_quests=None):
    """Render the main HUD bar showing player stats."""

    bar_height = 60
    bar = pygame.Surface((settings.SCREEN_WIDTH, bar_height), pygame.SRCALPHA)
    bar.fill(UI_BG)
    hour = int(player.time) // 60
    minute = int(player.time) % 60
    time_str = f"{hour:02d}:{minute:02d}"
    o_exp, o_need = job_progress(player, "office")
    d_exp, d_need = job_progress(player, "dealer")
    c_exp, c_need = job_progress(player, "clinic")
    office_prog = f"{o_exp}/{o_need}" if o_need else "MAX"
    dealer_prog = f"{d_exp}/{d_need}" if d_need else "MAX"
    clinic_prog = f"{c_exp}/{c_need}" if c_need else "MAX"
    job_info = (
        f"Office:{get_job_title(player, 'office')} "
        f"L{player.office_level}({office_prog})  "
        f"Dealer:{get_job_title(player, 'dealer')} "
        f"L{player.dealer_level}({dealer_prog})  "
        f"Clinic:{get_job_title(player, 'clinic')} "
        f"L{player.clinic_level}({clinic_prog})"
    )
    text = font.render(
        f"Money: ${int(player.money)}  Tokens: {player.tokens}  "
        f"Energy: {int(player.energy)}  Health: {int(player.health)}  "
        f"STR:{player.strength} DEF:{player.defense} SPD:{player.speed} "
        f"INT:{player.intelligence} CHA:{player.charisma}  "
        f"{job_info}  Day: {player.day}  Time: {time_str}",
        True,
        FONT_COLOR,
    )
    bar.blit(text, (16, 6))
    if player.epithet:
        ep_txt = font.render(player.epithet, True, FONT_COLOR)
        bar.blit(ep_txt, (settings.SCREEN_WIDTH // 2 - ep_txt.get_width() // 2, 6))
    seed_total = sum(player.resources.get(f"{n}_seeds", 0) for n in CROPS)
    produce_total = sum(player.resources.get(n, 0) for n in CROPS)
    res_txt = font.render(
        f"M:{player.resources.get('metal', 0)} "
        f"C:{player.resources.get('cloth', 0)} "
        f"H:{player.resources.get('herbs', 0)} "
        f"S:{seed_total} P:{produce_total}",
        True,
        FONT_COLOR,
    )
    bar.blit(res_txt, (16, 20))
    crops_line = " ".join(
        f"{c['type']}:{min(player.day - c['planted_day'], CROPS[c['type']]['growth_days'])}/{CROPS[c['type']]['growth_days']}"
        for c in player.crops
    )
    if crops_line:
        crop_txt = font.render(crops_line, True, FONT_COLOR)
        bar.blit(crop_txt, (16, 32))
    rep_line = (
        f"Mayor:{player.reputation.get('mayor', 0)} "
        f"Biz:{player.reputation.get('business', 0)} "
        f"Gang:{player.reputation.get('gang', 0)}"
    )
    rewards = (
        factions.mayor_rewards(player)
        + factions.business_rewards(player)
        + factions.gang_rewards(player)
    )
    if rewards:
        rep_line += " " + ", ".join(rewards)
    rep_txt = font.render(rep_line, True, FONT_COLOR)
    bar.blit(rep_txt, (16, 44))
    card_stat = font.render(
        f"Cards: {len(player.cards)}/10",
        True,
        FONT_COLOR,
    )
    bar.blit(card_stat, (settings.SCREEN_WIDTH - card_stat.get_width() - 20, 20))
    if player.crafting_skills:
        first = next(iter(player.crafting_skills))
        level = player.crafting_skills[first]
        xp = player.crafting_exp.get(first, 0)
        needed = crafting_exp_needed(player, first)
        craft_prog = f"{first.title()} {level} {xp}/{needed}"
    else:
        craft_prog = "No Crafting"
    craft_txt = font.render(f"Craft XP: {craft_prog}", True, FONT_COLOR)
    bar.blit(craft_txt, (settings.SCREEN_WIDTH - craft_txt.get_width() - 20, 32))
    season_txt = font.render(f"{player.season} - {player.weather}", True, FONT_COLOR)
    bar.blit(season_txt, (settings.SCREEN_WIDTH // 2 - season_txt.get_width() // 2, 32))
    if player.companion:
        ctxt = font.render(f"Pet: {player.companion}", True, FONT_COLOR)
        bar.blit(ctxt, (settings.SCREEN_WIDTH - ctxt.get_width() - 20, 6))
    # progress bars for energy and health
    pygame.draw.rect(bar, (80, 80, 80), (16, 44, 100, 10))
    pygame.draw.rect(bar, (0, 200, 0), (16, 44, int(player.energy), 10))
    pygame.draw.rect(bar, (80, 80, 80), (140, 44, 100, 10))
    pygame.draw.rect(bar, (200, 0, 0), (140, 44, int(player.health), 10))
    e_txt = font.render("E", True, FONT_COLOR)
    h_txt = font.render("H", True, FONT_COLOR)
    bar.blit(e_txt, (6, 42))
    bar.blit(h_txt, (130, 42))
    heavy_cd = (
        player.ability_cooldowns["heavy"] // 60
        if player.ability_cooldowns["heavy"]
        else "R"
    )
    guard_cd = (
        player.ability_cooldowns["guard"] // 60
        if player.ability_cooldowns["guard"]
        else "R"
    )
    special_cd = (
        player.ability_cooldowns["special"] // 60
        if player.ability_cooldowns["special"]
        else "R"
    )
    cd_txt = font.render(
        f"Z:{heavy_cd} X:{guard_cd} C:{special_cd}", True, FONT_COLOR
    )
    bar.blit(cd_txt, (settings.SCREEN_WIDTH - cd_txt.get_width() - 20, 32))
    surface.blit(bar, (0, 0))

    # Show current quest below the stat bar
    quest_text = None
    if player.side_quest:
        sq = SIDE_QUESTS.get(player.side_quest)
        if sq:
            quest_text = sq.description
    if quest_text is None:
        if story_quests and player.story_stage < len(story_quests):
            quest_text = story_quests[player.story_stage].description
        elif player.current_quest < len(quests):
            quest_text = quests[player.current_quest].description
    if quest_text:
        qsurf = font.render(f"Quest: {quest_text}", True, FONT_COLOR)
        qbg = pygame.Surface(
            (qsurf.get_width() + 12, qsurf.get_height() + 4), pygame.SRCALPHA
        )
        qbg.fill((255, 255, 255, 220))
        surface.blit(qbg, (16, bar_height + 4))
        surface.blit(qsurf, (22, bar_height + 6))



def draw_inventory_screen(surface, font, player, slot_rects, item_rects, dragging, hotkey_rects=None, furn_rects=None):
    """Display the inventory screen with equipment and items."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 120, settings.SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Inventory", True, FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    for slot, rect in slot_rects.items():
        pygame.draw.rect(surface, (210, 210, 210), rect)
        label = font.render(slot.title(), True, FONT_COLOR)
        surface.blit(label, (rect.x + 2, rect.y - 20))
        item = player.equipment.get(slot)
        if item:
            it = font.render(
                f"{item.name} Lv{item.level} A{item.attack} D{item.defense} "
                f"S{item.speed} C{item.combo}",
                True,
                FONT_COLOR,
            )
            surface.blit(it, (rect.x + 4, rect.y + 20))

    for rect, item in item_rects:
        pygame.draw.rect(surface, (200, 220, 230), rect)
        txt = font.render(
            f"{item.name} Lv{item.level} A{item.attack} D{item.defense} "
            f"S{item.speed} C{item.combo}",
            True,
            FONT_COLOR,
        )
        surface.blit(txt, (rect.x + 4, rect.y + 20))

    if dragging:
        item, pos = dragging
        txt = font.render(
            f"{item.name} Lv{item.level} A{item.attack} D{item.defense} "
            f"S{item.speed} C{item.combo}",
            True,
            FONT_COLOR,
        )
        bg = pygame.Surface((60, 60), pygame.SRCALPHA)
        bg.fill((230, 230, 240, 200))
        bg_rect = bg.get_rect(center=pos)
        surface.blit(bg, bg_rect.topleft)
        surface.blit(txt, (bg_rect.x + 4, bg_rect.y + 20))

    produce_total = sum(player.resources.get(n, 0) for n in CROPS)
    res = (
        f"Metal:{player.resources.get('metal', 0)} "
        f"Cloth:{player.resources.get('cloth', 0)} "
        f"Herbs:{player.resources.get('herbs', 0)} "
        f"Produce:{produce_total}"
    )
    res_txt = font.render(res, True, FONT_COLOR)
    surface.blit(res_txt, (100, settings.SCREEN_HEIGHT - 120))
    card_line = ", ".join(player.cards) if player.cards else "None"
    card_txt = font.render(
        f"Cards ({len(player.cards)}/10): {card_line}", True, FONT_COLOR
    )
    surface.blit(card_txt, (100, settings.SCREEN_HEIGHT - 100))

    if hotkey_rects:
        for i, rect in enumerate(hotkey_rects):
            pygame.draw.rect(surface, (210, 210, 210), rect)
            label = font.render(str(i + 1), True, FONT_COLOR)
            surface.blit(label, (rect.x + 2, rect.y - 20))
            item = player.hotkeys[i]
            if item:
                txt = font.render(item.name, True, FONT_COLOR)
                surface.blit(txt, (rect.x + 4, rect.y + 14))

    if furn_rects:
        for idx, rect in enumerate(furn_rects):
            pygame.draw.rect(surface, (200, 190, 150), rect)
            label = font.render(f"F{idx+1}", True, FONT_COLOR)
            surface.blit(label, (rect.x + 2, rect.y - 20))
            slot = f"slot{idx+1}"
            item = player.furniture.get(slot)
            if item:
                txt = font.render(item.name, True, FONT_COLOR)
                surface.blit(txt, (rect.x + 4, rect.y + 20))


def draw_perk_menu(surface, font, player, perks):
    """Render the perk selection menu."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 120, settings.SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Choose a Perk", True, FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    for i, (name, desc) in enumerate(perks):
        level = player.perk_levels.get(name, 0)
        txt = font.render(
            f"{i+1}: {name} Lv{level}/{PERK_MAX_LEVEL} - {desc}", True, FONT_COLOR
        )
        surface.blit(txt, (100, 120 + i * 40))

    info = font.render(f"Points: {player.perk_points}   [Q] Exit", True, FONT_COLOR)
    surface.blit(info, (100, 120 + len(perks) * 40 + 20))


def draw_companion_menu(surface, font, player, abilities):
    """Render the companion training menu."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 120, settings.SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Train Companion", True, FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    levels = player.companion_abilities.get(player.companion, {})
    y = 100
    active = next(
        (q for q in COMPANION_QUESTS.values() if q and q.name == player.side_quest),
        None,
    )
    if active:
        qtxt = font.render(f"Quest: {active.description}", True, FONT_COLOR)
        surface.blit(qtxt, (100, y))
        y += 20
    morale_txt = font.render(f"Morale: {player.companion_morale}", True, FONT_COLOR)
    surface.blit(morale_txt, (100, y))
    offset = 20
    for i, (name, desc, _stat) in enumerate(abilities):
        lvl = levels.get(name, 0)
        txt = font.render(
            f"{i+1}: {name} Lv{lvl}/{PERK_MAX_LEVEL} - {desc}", True, FONT_COLOR
        )
        surface.blit(txt, (100, y + 20 + i * 40))

    info = font.render("[Q] Exit", True, FONT_COLOR)
    surface.blit(info, (100, y + 20 + len(abilities) * 40 + offset))


def draw_quest_log(surface, font, quests, player, story_quests=None):
    """Show completed and active quests."""
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 120, settings.SCREEN_HEIGHT - 120))
    panel.fill((240, 240, 220))
    surface.blit(panel, (60, 60))

    title = font.render("Quest Log", True, FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 70))

    y = 120
    if player.side_quest:
        hdr = font.render("Side Quest", True, FONT_COLOR)
        surface.blit(hdr, (100, y))
        y += 30
        sq = SIDE_QUESTS.get(player.side_quest)
        if sq:
            txt = font.render(f"[ ] {sq.description}", True, FONT_COLOR)
            surface.blit(txt, (120, y))
            y += 40
    if story_quests:
        hdr = font.render("Story Quests", True, FONT_COLOR)
        surface.blit(hdr, (100, y))
        y += 30
        for q in story_quests:
            status = "[x]" if q.completed else "[ ]"
            txt = font.render(f"{status} {q.description}", True, FONT_COLOR)
            surface.blit(txt, (120, y))
            y += 30
        y += 20
    for q in quests:
        status = "[x]" if q.completed else "[ ]"
        txt = font.render(f"{status} {q.description}", True, FONT_COLOR)
        surface.blit(txt, (100, y))
        y += 30

    note = font.render("Press L or Q to close", True, FONT_COLOR)
    surface.blit(note, (100, settings.SCREEN_HEIGHT - 140))


def draw_help_screen(surface, font):
    """Show a simple overlay listing the main controls."""
    overlay = pygame.Surface(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    panel = pygame.Surface((settings.SCREEN_WIDTH - 160, settings.SCREEN_HEIGHT - 160))
    panel.fill((240, 240, 220))
    surface.blit(panel, (80, 80))

    title = font.render("Help & Controls", True, FONT_COLOR)
    surface.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    lines = [
        "Move: Arrow keys/WASD",
        "Interact: E    Leave building: Q",
        "Inventory: I    Perks: P    Quest Log: L",
        "Save: F5    Load: F9    Toggle Help: F1",
        "Fullscreen: F11    Mute Audio: M",
        "Abilities: Z Heavy  X Guard  C Special",
    ]
    y = 160
    for line in lines:
        txt = font.render(line, True, FONT_COLOR)
        surface.blit(txt, (120, y))
        y += 40

    note = font.render("Press F1 or Q to close", True, FONT_COLOR)
    surface.blit(note, (120, y))


def draw_tip_panel(surface, font, text):
    """Display an instruction panel at the bottom of the screen."""
    panel_height = int(settings.SCREEN_HEIGHT * 0.0833)
    panel = pygame.Surface((settings.SCREEN_WIDTH, panel_height))
    panel.fill((245, 245, 200))
    surface.blit(panel, (0, settings.SCREEN_HEIGHT - panel_height))
    tip_surf = font.render(text, True, (80, 40, 40))
    surface.blit(
        tip_surf,
        (
            int(settings.SCREEN_WIDTH * 0.0125),
            settings.SCREEN_HEIGHT - panel_height + int(panel_height * 0.2),
        ),
    )


def draw_hotkey_bar(surface, font, player, rects):
    """Render hotkey slots showing bound items."""
    for i, rect in enumerate(rects):
        pygame.draw.rect(surface, (210, 210, 210), rect)
        label = font.render(str(i + 1), True, FONT_COLOR)
        surface.blit(
            label,
            (rect.x + int(rect.width * 0.033), rect.y - int(rect.height * 0.45)),
        )
        item = player.hotkeys[i]
        if item:
            txt = font.render(item.name, True, FONT_COLOR)
            surface.blit(
                txt,
                (rect.x + int(rect.width * 0.067), rect.y + int(rect.height * 0.25)),
            )


def draw_home_interior(surface, font, player, frame, bed_rect, door_rect, furn_rects):
    """Draw a simple interior of the player's home."""
    surface.fill((235, 225, 200))
    # walls
    wall = int(settings.SCREEN_WIDTH * 0.025)
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, settings.SCREEN_WIDTH, wall))
    pygame.draw.rect(
        surface,
        (160, 140, 110),
        (0, settings.SCREEN_HEIGHT - wall, settings.SCREEN_WIDTH, wall),
    )
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, wall, settings.SCREEN_HEIGHT))
    pygame.draw.rect(
        surface,
        (160, 140, 110),
        (settings.SCREEN_WIDTH - wall, 0, wall, settings.SCREEN_HEIGHT),
    )

    # bed
    pygame.draw.rect(surface, (200, 70, 70), bed_rect)
    pygame.draw.rect(
        surface,
        (255, 255, 255),
        bed_rect.inflate(
            -int(bed_rect.width * 0.09), -int(bed_rect.height * 0.167)
        ),
    )

    # door
    pygame.draw.rect(surface, (100, 80, 60), door_rect)
    knob_x = door_rect.right - int(door_rect.width * 0.167)
    knob_r = max(1, int(door_rect.width * 0.05))
    pygame.draw.circle(surface, (220, 210, 120), (knob_x, door_rect.centery), knob_r)

    for idx, rect in enumerate(furn_rects):
        pygame.draw.rect(surface, (200, 190, 150), rect)
        slot = f"slot{idx+1}"
        item = player.furniture.get(slot)
        if item:
            txt = font.render(item.name, True, FONT_COLOR)
            surface.blit(
                txt,
                (rect.x + int(rect.width * 0.033), rect.y + int(rect.height * 0.25)),
            )

    draw_player_sprite(
        surface, player.rect, frame, player.facing_left, player.color, player.head_color
    )


def load_forest_enemy_images():
    """Load images for enemies in the forest area."""
    if FOREST_ENEMY_IMAGES:
        return FOREST_ENEMY_IMAGES
    for i in range(3):
        path = os.path.join(settings.IMAGE_DIR, f"enemy_{i}.png")
        if os.path.exists(path):
            FOREST_ENEMY_IMAGES.append(pygame.image.load(path).convert_alpha())
        else:
            s = pygame.Surface((60, 60))
            s.fill((200, 0, 0))
            FOREST_ENEMY_IMAGES.append(s)
    return FOREST_ENEMY_IMAGES


def draw_forest_area(surface, font, player, frame, enemy_rects, door_rect):
    """Draw the separate forest combat area."""
    surface.fill((50, 140, 70))

    pygame.draw.rect(surface, (100, 80, 60), door_rect)
    knob_x = door_rect.right - int(door_rect.width * 0.167)
    knob_r = max(1, int(door_rect.width * 0.05))
    pygame.draw.circle(surface, (220, 210, 120), (knob_x, door_rect.centery), knob_r)

    images = load_forest_enemy_images()
    for rect, img in zip(enemy_rects, images):
        surface.blit(img, rect)

    draw_player_sprite(
        surface, player.rect, frame, player.facing_left, player.color, player.head_color
    )


def draw_bar_interior(
    surface,
    font,
    player,
    frame,
    counter_rect,
    bj_rect,
    slot_rect,
    dart_rect,
    brawl_rect,
    door_rect,
):
    """Draw the interior of the bar with simple interaction spots."""
    surface.fill((225, 205, 170))

    wall = int(settings.SCREEN_WIDTH * 0.025)
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, settings.SCREEN_WIDTH, wall))
    pygame.draw.rect(
        surface,
        (160, 140, 110),
        (0, settings.SCREEN_HEIGHT - wall, settings.SCREEN_WIDTH, wall),
    )
    pygame.draw.rect(surface, (160, 140, 110), (0, 0, wall, settings.SCREEN_HEIGHT))
    pygame.draw.rect(
        surface,
        (160, 140, 110),
        (settings.SCREEN_WIDTH - wall, 0, wall, settings.SCREEN_HEIGHT),
    )

    # counter for buying tokens
    pygame.draw.rect(surface, (120, 80, 60), counter_rect)
    pygame.draw.rect(
        surface,
        (180, 140, 100),
        counter_rect.inflate(
            -int(counter_rect.width * 0.111), -int(counter_rect.height * 0.167)
        ),
    )
    ct = font.render("Tokens", True, FONT_COLOR)
    surface.blit(
        ct,
        (
            counter_rect.x + int(counter_rect.width * 0.111),
            counter_rect.y + counter_rect.height // 2 - ct.get_height() // 2,
        ),
    )

    # blackjack table
    pygame.draw.rect(surface, (60, 120, 60), bj_rect)
    bj = font.render("Blackjack", True, (250, 250, 250))
    surface.blit(
        bj,
        (
            bj_rect.x + int(bj_rect.width * 0.1),
            bj_rect.y + bj_rect.height // 2 - bj.get_height() // 2,
        ),
    )

    # slots
    pygame.draw.rect(surface, (90, 90, 150), slot_rect)
    sl = font.render("Slots", True, (250, 250, 250))
    surface.blit(
        sl,
        (
            slot_rect.x + int(slot_rect.width * 0.111),
            slot_rect.y + slot_rect.height // 2 - sl.get_height() // 2,
        ),
    )

    # darts board
    pygame.draw.rect(surface, (120, 70, 120), dart_rect)
    dr = font.render("Darts", True, (250, 250, 250))
    surface.blit(
        dr,
        (
            dart_rect.x + int(dart_rect.width * 0.1),
            dart_rect.y + dart_rect.height // 2 - dr.get_height() // 2,
        ),
    )

    # fighting ring
    pygame.draw.rect(surface, (180, 70, 70), brawl_rect)
    fb = font.render("Fight", True, (250, 250, 250))
    surface.blit(
        fb,
        (
            brawl_rect.x + int(brawl_rect.width * 0.125),
            brawl_rect.y + brawl_rect.height // 2 - fb.get_height() // 2,
        ),
    )

    pygame.draw.rect(surface, (100, 80, 60), door_rect)
    knob_x = door_rect.right - int(door_rect.width * 0.167)
    knob_r = max(1, int(door_rect.width * 0.05))
    pygame.draw.circle(surface, (220, 210, 120), (knob_x, door_rect.centery), knob_r)

    draw_player_sprite(
        surface, player.rect, frame, player.facing_left, player.color, player.head_color
    )
