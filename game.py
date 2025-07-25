"""Main game loop and event handling."""
import sys
import random
import pygame

from entities import (
    Player,
    Building,
    InventoryItem,
)
from rendering import (
    draw_player_sprite,
    load_player_sprites,
    draw_building,
    draw_road_and_sidewalks,
    draw_city_walls,
    draw_day_night,
    draw_weather,
    draw_ui,
    draw_inventory_screen,
    draw_perk_menu,
    draw_quest_log,
    draw_home_interior,
    draw_bar_interior,
    draw_forest_area,
    draw_sky,
    draw_npc,
    draw_tip_panel,
    draw_decorations,
    draw_hotkey_bar,
    draw_help_screen,
    draw_quest_marker,
)
from inventory import (
    SHOP_ITEMS,
    HOME_UPGRADES,
    COMPANIONS,
    buy_shop_item,
    buy_home_upgrade,
    bank_deposit,
    bank_withdraw,
    adopt_companion,
    train_companion,
    plant_seed,
    harvest_crops,
    sell_produce,
    gain_crafting_exp,
)
from businesses import BUSINESSES, buy_business, manage_business
from loaders import load_buildings
from combat import (
    energy_cost,
    fight_brawler,
    fight_enemy,
    fight_forest_enemy,
    fight_final_boss,
)
from quests import (
    QUESTS,
    SIDE_QUEST,
    NPC_QUEST,
    MALL_QUEST,
    NPCS,
    STORY_QUESTS,
    check_quests,
    check_perk_unlocks,
    check_hidden_perks,
    check_achievements,
    random_event,
    update_npcs,
    advance_story,
    check_story,
)

from careers import work_job, get_job_title, job_pay
from constants import PERK_MAX_LEVEL

import settings
from settings import (
    MAP_WIDTH,
    MAP_HEIGHT,
    PLAYER_SIZE,
    PLAYER_SPEED,
    SKATEBOARD_SPEED_MULT,
    MINUTES_PER_FRAME,
    MUSIC_FILE,
    STEP_SOUND_FILE,
    ENTER_SOUND_FILE,
    QUEST_SOUND_FILE,
    MUSIC_VOLUME,
    SFX_VOLUME,
)

from helpers import (
    recalc_layouts,
    compute_slot_rects,
    compute_hotkey_rects,
    compute_furniture_rects,
    init_furniture_positions,
    quest_target_building,
    building_open,
    update_weather,
    advance_day,
    sleep,
    play_blackjack,
    play_slots,
    play_darts,
    go_fishing,
    solve_puzzle,
    dig_for_treasure,
    card_duel,
    
    save_game,
    load_game,
    HOME_WIDTH,
    HOME_HEIGHT,
    BED_RECT,
    DOOR_RECT,
    BAR_WIDTH,
    BAR_HEIGHT,
    BAR_DOOR_RECT,
    COUNTER_RECT,
    BJ_RECT,
    SLOT_RECT,
    BRAWL_RECT,
    DART_RECT,
    FOREST_WIDTH,
    FOREST_HEIGHT,
    FOREST_DOOR_RECT,
)
from menus import start_menu, character_creation

recalc_layouts()


pygame.init()
try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False
    print("Audio disabled: mixer could not initialize")

BUILDINGS = load_buildings()

FOREST_ENEMY_RECTS = [
    pygame.Rect(300, 300, 60, 60),
    pygame.Rect(700, 300, 60, 60),
    pygame.Rect(500, 500, 60, 60),
]



# Random events that may occur while exploring
def _ev_found_money(p: Player) -> None:
    """Give the player money found on the ground."""
    p.money += 5
    bonus = 5 * p.perk_levels.get("Lucky", 0)
    p.money += 5 + bonus


def _ev_gain_int(p: Player) -> None:
    """Increase the player's intelligence."""
    p.intelligence += 1
    p.intelligence += 1 + p.perk_levels.get("Lucky", 0)


def _ev_gain_cha(p: Player) -> None:
    """Increase the player's charisma."""
    p.charisma += 1
    p.charisma += 1 + p.perk_levels.get("Lucky", 0)


def _ev_trip(p: Player) -> None:
    """Cause the player to lose a small amount of health."""
    p.health = max(p.health - 5, 0)


def _ev_theft(p: Player) -> None:
    """Steal money from the player."""
    p.money = max(p.money - 10, 0)


def _ev_free_food(p: Player) -> None:
    """Restore some of the player's energy."""
    p.energy = min(100, p.energy + 10 + 2 * p.perk_levels.get("Lucky", 0))


def _ev_help_reward(p: Player) -> None:
    """Reward the player for helping someone."""
    p.money += 15 + 5 * p.perk_levels.get("Lucky", 0)


def _ev_found_token(p: Player) -> None:
    """Grant the player a casino token."""
    p.tokens += 1


def _ev_found_metal(p: Player) -> None:
    """Give the player a piece of scrap metal."""
    p.resources["metal"] = p.resources.get("metal", 0) + 1


def _ev_found_cloth(p: Player) -> None:
    """Give the player a piece of cloth."""
    p.resources["cloth"] = p.resources.get("cloth", 0) + 1



# Items sold at the shop: name, cost, and effect function
# Perks that can be unlocked with perk points
# Each perk can be upgraded up to PERK_MAX_LEVEL levels
PERKS = [
    ("Gym Rat", "STR training gives +1 per level"),
    ("Book Worm", "INT studying gives +1 per level"),
    ("Social Butterfly", "CHA chatting gives +1 per level"),
    ("Night Owl", "Sleeping restores +10 energy per level"),
    ("Lucky", "Random events yield extra rewards"),
    ("Iron Will", "Energy costs reduced 5% per level"),
]

# Special hidden perks unlocked through achievements
SECRET_PERKS = [
    ("Bar Champion", "Win all 5 brawls"),
    ("Home Owner", "Own every home upgrade"),
    ("Perk Master", "Max out every other perk"),
    ("Champion", "Defeat the final boss"),
]

# Maximum hearts an NPC can have
MAX_HEARTS = 10



def main():
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE
    )
    pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    if start_menu(screen, font):
        loaded = load_game()
    else:
        loaded = None

    if SOUND_ENABLED:
        step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
        enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
        quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
        for snd in (step_sound, enter_sound, quest_sound):
            snd.set_volume(SFX_VOLUME)
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
    else:
        step_sound = enter_sound = quest_sound = None

    if loaded:
        player = loaded
    else:
        name, color, head_color = character_creation(screen, font)
        player = Player(
            pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE),
            name=name,
            color=color,
            head_color=head_color,
        )
        pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)

        if start_menu(self.screen, self.font):
            loaded = load_game()
        else:
            loaded = None

        if SOUND_ENABLED:
            self.step_sound = pygame.mixer.Sound(STEP_SOUND_FILE)
            self.enter_sound = pygame.mixer.Sound(ENTER_SOUND_FILE)
            self.quest_sound = pygame.mixer.Sound(QUEST_SOUND_FILE)
            for snd in (self.step_sound, self.enter_sound, self.quest_sound):
                snd.set_volume(SFX_VOLUME)
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
        else:
            self.step_sound = self.enter_sound = self.quest_sound = None

        if loaded:
            self.player = loaded
        else:
            name, color, head_color = character_creation(self.screen, self.font)
            self.player = Player(
                pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE),
                name=name,
                color=color,
                head_color=head_color,
            )


    while True:
        frame += 1
        player.time += MINUTES_PER_FRAME
        if player.time >= 1440:
            player.time -= 1440
            advance_day(player)
        update_npcs()
        for ab, cd in player.ability_cooldowns.items():
            if cd > 0:
                player.ability_cooldowns[ab] -= 1
        advance_story(player)
        check_story(player)
        if check_perk_unlocks(player):
            shop_message = "Gained a perk point! Press P to spend"
            shop_message_timer = 90
        secret = check_hidden_perks(player)
        if secret:
            shop_message = secret
            shop_message_timer = 90
        achieve = check_achievements(player)
        if achieve:
            shop_message = achieve
            shop_message_timer = 90
        item_rects = []
        if show_inventory:
            for i, item in enumerate(player.inventory):
                col = i % 5
                row = i // 5
                item_rects.append(
                    (pygame.Rect(320 + col * 120, 150 + row * 70, 100, 60), item)
                )
        for event in pygame.event.get():
            if show_help:
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_F1,
                    pygame.K_q,
                ):
                    show_help = False
                continue
            if event.type == pygame.QUIT:
                save_game(player)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    save_game(player)
                    shop_message = "Game saved!"
                    shop_message_timer = 60
                elif event.key == pygame.K_F9:
                    loaded = load_game()
                    if loaded:
                        player = loaded
                        shop_message = "Game loaded!"
                    else:
                        shop_message = "No save found!"
                    shop_message_timer = 60
                elif event.key == pygame.K_i:
                    show_inventory = not show_inventory
                    dragging_item = None
                elif event.key == pygame.K_p and player.perk_points > 0:
                    show_perk_menu = not show_perk_menu
                    dragging_item = None
                elif event.key == pygame.K_l:
                    show_log = not show_log
                    dragging_item = None
                elif event.key == pygame.K_F1:
                    show_help = True
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
                    screen = pygame.display.set_mode(
                        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), flags
                    )
                    recalc_layouts()
                    slot_rects = compute_slot_rects()
                    hotkey_rects = compute_hotkey_rects()
                elif event.key == pygame.K_m and SOUND_ENABLED:
                    muted = not muted
                    vol = 0 if muted else SFX_VOLUME
                    if step_sound:
                        for snd in (step_sound, enter_sound, quest_sound):
                            snd.set_volume(vol)
                        pygame.mixer.music.set_volume(0 if muted else MUSIC_VOLUME)
                    shop_message = "Sound muted" if muted else "Sound on"
                    shop_message_timer = 60
                elif (
                    event.key == pygame.K_h
                    and not show_inventory
                    and not show_log
                    and not in_building
                ):
                    pot = next(
                        (i for i in player.inventory if i.name == "Health Potion"), None
                    )
                    ener = next(
                        (i for i in player.inventory if i.name == "Energy Potion"), None
                    )
                    if pot:
                        player.inventory.remove(pot)
                        player.health = min(100, player.health + 30)
                        shop_message = "Drank Health Potion (+30 HP)"
                    elif ener:
                        player.inventory.remove(ener)
                        player.energy = min(100, player.energy + 30)
                        shop_message = "Drank Energy Potion (+30 EN)"
                    else:
                        shop_message = "No potion"
                    shop_message_timer = 60
                elif (
                    event.key == pygame.K_z
                    and not show_inventory
                    and not show_log
                    and not in_building
                ):
                    if player.ability_cooldowns["heavy"] == 0:
                        player.active_ability = "heavy"
                        player.ability_cooldowns["heavy"] = 300
                        shop_message = "Heavy Strike ready!"
                    else:
                        shop_message = "Heavy Strike cooling"
                    shop_message_timer = 60
                elif (
                    event.key == pygame.K_x
                    and not show_inventory
                    and not show_log
                    and not in_building
                ):
                    if player.ability_cooldowns["guard"] == 0:
                        player.active_ability = "guard"
                        player.ability_cooldowns["guard"] = 300
                        shop_message = "Guard Stance ready!"
                    else:
                        shop_message = "Guard Stance cooling"
                    shop_message_timer = 60
                elif (
                    pygame.K_1 <= event.key <= pygame.K_5
                    and not show_inventory
                    and not show_log
                    and not in_building
                ):
                    idx = event.key - pygame.K_1
                    if idx < len(player.hotkeys) and player.hotkeys[idx]:
                        item = player.hotkeys[idx]
                        if item.name in ("Cola", "Energy Potion"):
                            gain = 30 if item.name == "Energy Potion" else 5
                            player.energy = min(100, player.energy + gain)
                        elif item.name in ("Protein Bar", "Health Potion"):
                            gain = 30 if item.name == "Health Potion" else 5
                            player.health = min(100, player.health + gain)
                        elif item.name == "Fruit Pie":
                            player.energy = min(100, player.energy + 10)
                            player.health = min(100, player.health + 10)
                        player.hotkeys[idx] = None
                        shop_message = f"Used {item.name}"
                    else:
                        shop_message = "No item"
                    shop_message_timer = 60
                elif (
                    event.key == pygame.K_t
                    and not in_building
                    and not show_inventory
                    and not show_log
                ):
                    player.time += 180
                    if player.time >= 1440:
                        player.time -= 1440
                        advance_day(player)
                    shop_message = "Skipped ahead 3 hours"
                    shop_message_timer = 60
            if show_inventory:
                furn_rects = compute_furniture_rects(player)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    handled = False
                    for i, (rect, item) in enumerate(item_rects):
                        if rect.collidepoint(pos):
                            dragging_item = item
                            drag_origin = ("inventory", i)
                            drag_pos = pos
                            player.inventory.pop(i)
                            handled = True
                            break
                    if not handled:
                        for slot, rect in slot_rects.items():
                            if rect.collidepoint(pos) and player.equipment.get(slot):
                                dragging_item = player.equipment[slot]
                                drag_origin = ("slot", slot)

                                drag_pos = pos
                                player.inventory.pop(i)
                                handled = True
                                break
                        if not handled:

                            for i, rect in enumerate(hotkey_rects):
                                if rect.collidepoint(pos) and player.hotkeys[i]:
                                    dragging_item = player.hotkeys[i]
                                    drag_origin = ("hotkey", i)

                                    drag_pos = pos
                                    player.equipment[slot] = None
                                    break

                        if not handled:
                            furn_rects = compute_furniture_rects(player)
                            for idx, rect in enumerate(furn_rects):
                                slot = f"slot{idx+1}"
                                if rect.collidepoint(pos) and player.furniture.get(
                                    slot
                                ):
                                    dragging_item = player.furniture[slot]
                                    drag_origin = ("furn", slot)
                                    drag_pos = pos
                                    player.furniture[slot] = None
                                    handled = True
                                    break
                elif event.type == pygame.MOUSEMOTION and dragging_item:
                    drag_pos = event.pos
                elif (
                    event.type == pygame.MOUSEBUTTONUP
                    and event.button == 1
                    and dragging_item
                ):
                    pos = event.pos
                    placed = False
                    for slot, rect in slot_rects.items():
                        if (
                            rect.collidepoint(pos)
                            and dragging_item.slot == slot
                            and player.equipment.get(slot) is None
                        ):
                            player.equipment[slot] = dragging_item
                            placed = True
                            break
                    if not placed:
                        for i, rect in enumerate(hotkey_rects):
                            if (
                                rect.collidepoint(pos)
                                and dragging_item.slot == "consumable"
                                and player.hotkeys[i] is None
                            ):
                                player.hotkeys[i] = dragging_item
                                placed = True
                                break
                    if not placed:
                        for idx, rect in enumerate(furn_rects):
                            if (
                                rect.collidepoint(pos)
                                and dragging_item.slot == "furniture"
                                and player.furniture.get(f"slot{idx+1}") is None
                            ):
                                player.furniture[f"slot{idx+1}"] = dragging_item
                                player.furniture_pos[f"slot{idx+1}"] = (rect.x, rect.y)
                                placed = True
                                break
                        if not placed:
                            for i, rect in enumerate(hotkey_rects):
                                if rect.collidepoint(pos) and dragging_item.slot == 'consumable' and player.hotkeys[i] is None:
                                    player.hotkeys[i] = dragging_item
                                    placed = True
                                    break
                        if not placed:
                            for idx, rect in enumerate(furn_rects):
                                if (
                                    rect.collidepoint(pos)
                                    and dragging_item.slot == 'furniture'
                                    and player.furniture.get(f'slot{idx+1}') is None
                                ):
                                    player.furniture[f'slot{idx+1}'] = dragging_item
                                    player.furniture_pos[f'slot{idx+1}'] = (rect.x, rect.y)
                                    placed = True
                                    break
                        if not placed:
                            player.inventory.append(dragging_item)
                        dragging_item = None
                if show_perk_menu and event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        if idx < len(PERKS):
                            name = PERKS[idx][0]
                            level = player.perk_levels.get(name, 0)
                            if level < PERK_MAX_LEVEL and player.perk_points > 0:
                                player.perk_levels[name] = level + 1
                                player.perk_points -= 1
                                shop_message = f"Perk upgraded: {name} Lv{level+1}"
                                shop_message_timer = 90
                            else:
                                shop_message = "Perk at max level"
                                shop_message_timer = 60
                        show_perk_menu = False
                    elif event.key in (pygame.K_q, pygame.K_p):
                        show_perk_menu = False
                if show_log and event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_l, pygame.K_q):
                        show_log = False
                if event.type == pygame.KEYDOWN and inside_home:
                    if event.key == pygame.K_e:
                        if player.rect.colliderect(BED_RECT):
                            extra = sleep(player)
                            shop_message = "You slept. New day!"
                            if extra:
                                shop_message += " " + extra
                            shop_message_timer = 60
                        elif player.rect.colliderect(DOOR_RECT):
                            inside_home = False
                            player.rect.topleft = home_return
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        avail = [u for u in HOME_UPGRADES if u[3] <= player.home_level]
                        idx = event.key - pygame.K_1
                        if idx < len(avail):
                            full_idx = HOME_UPGRADES.index(avail[idx])
                            shop_message = buy_home_upgrade(player, full_idx)
                        else:
                            shop_message = "Invalid choice"
                        shop_message_timer = 60
    
                if event.type == pygame.KEYDOWN and inside_bar:
                    if event.key == pygame.K_e:
                        if (
                            player.story_branch == "gang"
                            and player.side_quest == "Gang Package"
                            and player.rect.colliderect(COUNTER_RECT)
                        ):
                            player.side_quest = None
                            player.gang_package_done = True
                            shop_message = "You delivered the package"
                            shop_message_timer = 60
                            continue
                        if (
                            player.story_branch == "gang"
                            and player.story_stage == 3
                            and player.rect.colliderect(COUNTER_RECT)
                        ):
                            player.story_stage = 4
                            shop_message = "Gang Leader: Nice work"
                            shop_message_timer = 60
                            continue
                        if player.rect.colliderect(COUNTER_RECT):
                            if player.money >= 10:
                                player.money -= 10
                                player.tokens += 1
                                shop_message = "Bought a token"
                            else:
                                shop_message = "Need $10"
                        elif player.rect.colliderect(BJ_RECT):
                            shop_message = play_blackjack(player)
                        elif player.rect.colliderect(SLOT_RECT):
                            shop_message = play_slots(player)
                        elif player.rect.colliderect(DART_RECT):
                            shop_message = play_darts(player)
                        elif player.rect.colliderect(BRAWL_RECT):
                            shop_message = fight_brawler(player)
                        elif player.rect.colliderect(BAR_DOOR_RECT):
                            inside_bar = False
                            player.rect.topleft = bar_return
                        else:
                            shop_message = ""
                        shop_message_timer = 60
    
                if event.type == pygame.KEYDOWN and inside_forest:
                    if event.key == pygame.K_e:
                        for i, rect in enumerate(FOREST_ENEMY_RECTS):
                            if player.rect.colliderect(rect):
                                shop_message = fight_forest_enemy(player, i)
                                break
                        else:
                            if player.rect.colliderect(FOREST_DOOR_RECT):
                                inside_forest = False
                                player.rect.topleft = forest_return
                        shop_message_timer = 60
    
                if event.type == pygame.KEYDOWN and in_building:
                    if in_building == "job" and event.key == pygame.K_e:
                        shop_message = work_job(player, "office")
                        shop_message_timer = 60
                    elif in_building == "home":
                        player.energy = 100
                        player.time = 8 * 60
                        player.day += 1
                        shop_message = "You slept. New day!"
                        shop_message_timer = 60
                        if event.key == pygame.K_e:
                            extra = sleep(player)
                            shop_message = "You slept. New day!"
                            if extra:
                                shop_message += " " + extra
                            shop_message_timer = 60
                        elif pygame.K_1 <= event.key <= pygame.K_9:
                            idx = event.key - pygame.K_1
                            shop_message = buy_home_upgrade(player, idx)
                            shop_message_timer = 60
                        else:
                            continue
                    elif in_building == "shop":
                        if pygame.K_1 <= event.key <= pygame.K_9:
                            idx = event.key - pygame.K_1
                            shop_message = buy_shop_item(player, idx)
                            shop_message_timer = 60
                        elif event.key == pygame.K_0:
                            shop_message = buy_shop_item(player, 9)
                            shop_message_timer = 60
                        elif event.key == pygame.K_e:
                            shop_message = "Press number keys to buy"
                            shop_message_timer = 60
                        else:
                            continue
                    elif in_building == "gym" and event.key == pygame.K_e:
                        if player.side_quest == NPC_QUEST.name:
                            NPC_QUEST.reward(player)
                            player.side_quest = None
                            shop_message = "Delivered the package!"
                        elif player.money >= 10 and player.energy >= 10:
                            player.money -= 10
                            player.energy -= 10
                            player.energy -= energy_cost(player, 10)
                            player.health = min(player.health + 5, 100)
                            player.strength += 1
                            shop_message = "You worked out! +1 STR, +5 health"
                            bonus = player.perk_levels.get("Gym Rat", 0)
                            gain = 1 + bonus
                            player.strength += gain
                            msg_gain = f" +{gain} STR"
                            shop_message = "You worked out!" + msg_gain + ", +5 health"
                        elif player.money < 10:
                            shop_message = "Need $10 to train"
                        else:
                            shop_message = "Too tired to train!"
                        shop_message_timer = 60
                    elif in_building == "library" and event.key == pygame.K_e:
                        if player.money >= 5 and player.energy >= 5:
                            player.money -= 5
                            player.energy -= 5
                            player.intelligence += 1
                            shop_message = "You studied! +1 INT"
                            player.energy -= energy_cost(player, 5)
                            bonus = player.perk_levels.get("Book Worm", 0)
                            gain = 1 + bonus
                            player.intelligence += gain
                            msg_gain = f" +{gain} INT"
                            shop_message = "You studied!" + msg_gain
                            if player.side_quest == SIDE_QUEST.name:
                                SIDE_QUEST.reward(player)
                                player.side_quest = None
                                shop_message += " and delivered the papers"
                        elif player.money < 5:
                            shop_message = "Need $5 to study"
                        else:
                            shop_message = "Too tired to study!"
                        shop_message_timer = 60
                    elif in_building == "library" and event.key == pygame.K_p:
                        shop_message = solve_puzzle(player)
                        shop_message_timer = 60
                    elif in_building == "park" and event.key == pygame.K_e:
                        if player.energy >= 5:
                            player.energy -= 5
                            player.charisma += 1
                            shop_message = "You socialized! +1 CHA"
                            player.energy -= energy_cost(player, 5)
                            bonus = player.perk_levels.get("Social Butterfly", 0)
                            gain = 1 + bonus
                            if player.companion == "Peacock":
                                gain += player.companion_level
                            player.charisma += gain
                            msg_gain = f" +{gain} CHA"
                            shop_message = "You socialized!" + msg_gain
                        else:
                            shop_message = "Too tired to chat!"
                        shop_message_timer = 60
                    elif in_building == "park" and event.key == pygame.K_f:
                        shop_message = go_fishing(player)
                        shop_message_timer = 60

                    else:
                        continue
                elif in_building == "gym" and event.key == pygame.K_e:
                    if player.side_quest == NPC_QUEST.name:
                        NPC_QUEST.reward(player)
                        player.side_quest = None
                        shop_message = "Delivered the package!"
                    elif player.money >= 10 and player.energy >= 10:
                        player.money -= 10
                        player.energy -= 10
                        player.energy -= energy_cost(player, 10)
                        player.health = min(player.health + 5, 100)
                        player.strength += 1
                        shop_message = "You worked out! +1 STR, +5 health"
                        bonus = player.perk_levels.get("Gym Rat", 0)
                        gain = 1 + bonus
                        player.strength += gain
                        msg_gain = f" +{gain} STR"
                        shop_message = "You worked out!" + msg_gain + ", +5 health"
                    elif player.money < 10:
                        shop_message = "Need $10 to train"
                    else:
                        shop_message = "Too tired to train!"
                    shop_message_timer = 60
                elif in_building == "library" and event.key == pygame.K_e:
                    if player.money >= 5 and player.energy >= 5:
                        player.money -= 5
                        player.energy -= 5
                        player.intelligence += 1
                        shop_message = "You studied! +1 INT"
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Book Worm", 0)
                        gain = 1 + bonus
                        player.intelligence += gain
                        msg_gain = f" +{gain} INT"
                        shop_message = "You studied!" + msg_gain
                        if player.side_quest == SIDE_QUEST.name:
                            SIDE_QUEST.reward(player)
                            player.side_quest = None
                            shop_message += " and delivered the papers"
                    elif player.money < 5:
                        shop_message = "Need $5 to study"
                    else:
                        shop_message = "Too tired to study!"
                    shop_message_timer = 60
                elif in_building == "library" and event.key == pygame.K_p:
                    shop_message = solve_puzzle(player)
                    shop_message_timer = 60
                elif in_building == "park" and event.key == pygame.K_e:
                    if player.energy >= 5:
                        player.energy -= 5
                        player.charisma += 1
                        shop_message = "You socialized! +1 CHA"
                        player.energy -= energy_cost(player, 5)
                        bonus = player.perk_levels.get("Social Butterfly", 0)
                        gain = 1 + bonus
                        if player.companion == "Peacock":
                            gain += player.companion_level
                        player.charisma += gain
                        msg_gain = f" +{gain} CHA"
                        shop_message = "You socialized!" + msg_gain
                    else:
                        shop_message = "Too tired to chat!"
                    shop_message_timer = 60
                elif in_building == "park" and event.key == pygame.K_f:
                    shop_message = go_fishing(player)
                    shop_message_timer = 60
                elif in_building == "bar":
                    if event.key == pygame.K_b:
                        if player.money >= 10:
                            player.money -= 10
                            player.tokens += 1
                            shop_message = "Bought a token"
                        else:
                            shop_message = "Need $10"
                            shop_message = "Need $10"
                    elif event.key == pygame.K_j:
                        shop_message = play_blackjack(player)
                    elif event.key == pygame.K_s:
                        shop_message = play_slots(player)
                    elif event.key == pygame.K_d:
                        shop_message = play_darts(player)
                    elif event.key == pygame.K_f:
                        shop_message = fight_brawler(player)
                    elif event.key == pygame.K_e:
                        shop_message = "Buy tokens with B"  # hint when pressing E
                    else:
                        continue
                    shop_message_timer = 60
                elif in_building == "dungeon" and event.key == pygame.K_e:
                    shop_message = fight_enemy(player)
                    shop_message_timer = 60
                elif in_building == "boss" and event.key == pygame.K_e:
                    shop_message = fight_final_boss(player)
                    shop_message_timer = 60
                elif in_building == "forest" and event.key == pygame.K_e:
                    # fallback if player enters the woods via in_building
                    shop_message = fight_forest_enemy(player, random.randrange(3))
                    shop_message_timer = 60
                elif in_building == "petshop" and pygame.K_1 <= event.key <= pygame.K_6:
                    idx = event.key - pygame.K_1
                    shop_message = adopt_companion(player, idx)
                    shop_message_timer = 60
                elif in_building == "petshop" and event.key == pygame.K_t:
                    shop_message = train_companion(player)
                    shop_message_timer = 60
                elif in_building == "bank":
                    if event.key == pygame.K_e:
                        if not player.side_quest:
                            player.side_quest = SIDE_QUEST.name
                            shop_message = "Accepted delivery job!"

                        else:
                            continue
                        shop_message_timer = 60
                    elif in_building == "dungeon" and event.key == pygame.K_e:
                        shop_message = fight_enemy(player)
                        shop_message_timer = 60
                    elif in_building == "boss" and event.key == pygame.K_e:
                        shop_message = fight_final_boss(player)
                        shop_message_timer = 60
                    elif in_building == "forest" and event.key == pygame.K_e:
                        # fallback if player enters the woods via in_building
                        shop_message = fight_forest_enemy(player, random.randrange(3))
                        shop_message_timer = 60
                    elif in_building == "petshop" and pygame.K_1 <= event.key <= pygame.K_6:
                        idx = event.key - pygame.K_1
                        shop_message = adopt_companion(player, idx)
                        shop_message_timer = 60
                    elif in_building == "petshop" and event.key == pygame.K_t:
                        shop_message = train_companion(player)
                        shop_message_timer = 60
                    elif in_building == "bank":
                        if event.key == pygame.K_e:
                            if not player.side_quest:
                                player.side_quest = SIDE_QUEST.name
                                shop_message = "Accepted delivery job!"
                            else:
                                shop_message = "Talk to the librarian to finish"
                        elif event.key == pygame.K_d:
                            shop_message = bank_deposit(player)
                        elif event.key == pygame.K_w:
                            shop_message = bank_withdraw(player)
                        else:
                            continue
                        shop_message_timer = 60
                elif in_building == "mall" and event.key == pygame.K_c:
                    shop_message = card_duel(player)
                    shop_message_timer = 60
                elif in_building == "workshop":
                        if event.key == pygame.K_1:
                            if player.resources.get("herbs", 0) >= 2:
                                player.resources["herbs"] -= 2
                                player.inventory.append(
                                    InventoryItem("Health Potion", "consumable")
                                )
                                shop_message = "Crafted Health Potion"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 2 herbs"
                        elif event.key == pygame.K_2:
                            if player.resources.get("metal", 0) >= 3:
                                player.resources["metal"] -= 3
                                player.inventory.append(
                                    InventoryItem(
                                        "Iron Sword",
                                        "weapon",
                                        attack=4,
                                    )
                                )
                                shop_message = "Forged Iron Sword"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 3 metal"
                        elif event.key == pygame.K_3:
                            weapon = player.equipment.get("weapon")
                            if weapon and player.resources.get("metal", 0) >= 2:
                                player.resources["metal"] -= 2
                                weapon.attack += 1
                                weapon.level += 1
                                shop_message = "Upgraded weapon"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need weapon & 2 metal"
                        elif event.key == pygame.K_4:
                            armor = player.equipment.get("chest")
                            if armor and player.resources.get("cloth", 0) >= 2:
                                player.resources["cloth"] -= 2
                                armor.defense += 1
                                armor.level += 1
                                shop_message = "Upgraded armor"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need armor & 2 cloth"
                        elif event.key == pygame.K_5:
                            if player.crafting_level < 2:
                                shop_message = "Need Craft Lv2"
                            elif player.resources.get("metal", 0) >= 1 and player.resources.get("cloth", 0) >= 2:
                                player.resources["metal"] -= 1
                                player.resources["cloth"] -= 2
                                if "Decorations" not in player.home_upgrades:
                                    player.home_upgrades.append("Decorations")
                                    shop_message = "Built home decorations"
                                else:
                                    player.inventory.append(InventoryItem("Decor Chair", "furniture"))
                                    shop_message = "Crafted Decor Chair"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 1 metal & 2 cloth"
                        elif event.key == pygame.K_6:
                            if player.crafting_level < 2:
                                shop_message = "Need Craft Lv2"
                            elif player.resources.get("herbs", 0) >= 3:
                                player.resources["herbs"] -= 3
                                player.inventory.append(InventoryItem("Energy Potion", "consumable"))
                                shop_message = "Brewed Energy Potion"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 3 herbs"
                        elif event.key == pygame.K_7:
                            if player.crafting_level < 3:
                                shop_message = "Need Craft Lv3"
                            elif player.resources.get("metal", 0) >= 5 and player.resources.get("herbs", 0) >= 2:
                                player.resources["metal"] -= 5
                                player.resources["herbs"] -= 2
                                player.inventory.append(InventoryItem("Flaming Sword", "weapon", attack=6))
                                shop_message = "Forged Flaming Sword"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 5 metal & 2 herbs"
                        elif event.key == pygame.K_8:
                            if player.crafting_level < 3:
                                shop_message = "Need Craft Lv3"
                            elif player.resources.get("produce", 0) >= 2:
                                player.resources["produce"] -= 2
                                player.inventory.append(InventoryItem("Fruit Pie", "consumable"))
                                shop_message = "Baked Fruit Pie"
                                lvl_msg = gain_crafting_exp(player)
                                if lvl_msg:
                                    shop_message += f"  {lvl_msg}"
                            else:
                                shop_message = "Need 2 produce"
                        else:
                            continue
                        shop_message_timer = 60
                    elif in_building == "farm":
                        if event.key == pygame.K_p:
                            shop_message = plant_seed(player)
                        elif event.key == pygame.K_h:
                            shop_message = harvest_crops(player)
                        elif event.key == pygame.K_s:
                            shop_message = sell_produce(player)
                        else:

                            shop_message = "Need armor & 2 cloth"
                    elif event.key == pygame.K_5:
                        if player.crafting_level < 2:
                            shop_message = "Need Craft Lv2"
                        elif (
                            player.resources.get("metal", 0) >= 1
                            and player.resources.get("cloth", 0) >= 2
                        ):
                            player.resources["metal"] -= 1
                            player.resources["cloth"] -= 2
                            if "Decorations" not in player.home_upgrades:
                                player.home_upgrades.append("Decorations")
                                shop_message = "Built home decorations"
                            else:
                                player.inventory.append(
                                    InventoryItem("Decor Chair", "furniture")
                                )
                                shop_message = "Crafted Decor Chair"
                            lvl_msg = gain_crafting_exp(player)
                            if lvl_msg:
                                shop_message += f"  {lvl_msg}"
                        else:
                            shop_message = "Need 1 metal & 2 cloth"
                    elif event.key == pygame.K_6:
                        if player.crafting_level < 2:
                            shop_message = "Need Craft Lv2"
                        elif player.resources.get("herbs", 0) >= 3:
                            player.resources["herbs"] -= 3
                            player.inventory.append(
                                InventoryItem("Energy Potion", "consumable")
                            )
                            shop_message = "Brewed Energy Potion"
                            lvl_msg = gain_crafting_exp(player)
                            if lvl_msg:
                                shop_message += f"  {lvl_msg}"
                        else:
                            shop_message = "Need 3 herbs"
                    elif event.key == pygame.K_7:
                        if player.crafting_level < 3:
                            shop_message = "Need Craft Lv3"
                        elif (
                            player.resources.get("metal", 0) >= 5
                            and player.resources.get("herbs", 0) >= 2
                        ):
                            player.resources["metal"] -= 5
                            player.resources["herbs"] -= 2
                            player.inventory.append(
                                InventoryItem("Flaming Sword", "weapon", attack=6)
                            )
                            shop_message = "Forged Flaming Sword"
                            lvl_msg = gain_crafting_exp(player)
                            if lvl_msg:
                                shop_message += f"  {lvl_msg}"
                        else:
                            shop_message = "Need 5 metal & 2 herbs"
                    elif event.key == pygame.K_8:
                        if player.crafting_level < 3:
                            shop_message = "Need Craft Lv3"
                        elif player.resources.get("produce", 0) >= 2:
                            player.resources["produce"] -= 2
                            player.inventory.append(
                                InventoryItem("Fruit Pie", "consumable")
                            )
                            shop_message = "Baked Fruit Pie"
                            lvl_msg = gain_crafting_exp(player)
                            if lvl_msg:
                                shop_message += f"  {lvl_msg}"

                        else:
                            shop_message = "Too tired to help"
                        shop_message_timer = 60
                    elif in_building == "townhall":
                        if player.story_stage == 0 and event.key == pygame.K_e:
                            player.story_stage = 1
                            shop_message = "Mayor: Help clean up the city? Y/N"
                        elif player.story_stage == 1 and event.key == pygame.K_y:
                            player.story_branch = "mayor"
                            player.story_stage = 2
                            shop_message = "Mayor: Defeat 3 thugs in the alley."
                        elif player.story_stage == 1 and event.key == pygame.K_n:
                            player.story_branch = "gang"
                            player.story_stage = 2
                            player.side_quest = "Gang Package"
                            shop_message = "A shady figure gives you a package."
                        elif (
                            player.story_branch == "mayor"
                            and player.story_stage == 3
                            and event.key == pygame.K_e
                        ):
                            player.story_stage = 4
                            shop_message = "Mayor: Thank you for your help!"
                        else:
                            continue
                        shop_message_timer = 90
                    elif in_building == "dealer" and event.key == pygame.K_e:
                        shop_message = work_job(player, "dealer")
                        shop_message_timer = 60
                    elif in_building == "clinic" and event.key == pygame.K_e:
                        shop_message = work_job(player, "clinic")
                        shop_message_timer = 60
                    elif in_building == "clinic" and event.key == pygame.K_h:
                        if player.money >= 20 and (
                            player.health < 100 or player.energy < 100
                        ):
                            player.money -= 20
                            player.health = 100
                            player.energy = 100
                            shop_message = "Treatment complete"
                        elif player.money < 20:
                            shop_message = "Need $20"
                        else:
                            shop_message = "Already healthy"
                        shop_message_timer = 60
    
        dx = dy = 0
        keys = pygame.key.get_pressed()
        speed = PLAYER_SPEED
        if player.has_skateboard and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            speed = int(PLAYER_SPEED * SKATEBOARD_SPEED_MULT)
        if inside_home and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed
            if dx < 0:
                player.facing_left = True
            elif dx > 0:
                player.facing_left = False

            next_rect = player.rect.move(dx, dy)
            if (
                40 <= next_rect.x <= HOME_WIDTH - PLAYER_SIZE - 40
                and 40 <= next_rect.y <= HOME_HEIGHT - PLAYER_SIZE - 40
            ):
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif inside_bar and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed
            if dx < 0:
                player.facing_left = True
            elif dx > 0:
                player.facing_left = False

            next_rect = player.rect.move(dx, dy)
            if (
                40 <= next_rect.x <= BAR_WIDTH - PLAYER_SIZE - 40
                and 40 <= next_rect.y <= BAR_HEIGHT - PLAYER_SIZE - 40
            ):
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif inside_forest and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed
            if dx < 0:
                player.facing_left = True
            elif dx > 0:
                player.facing_left = False

            next_rect = player.rect.move(dx, dy)
            if (
                40 <= next_rect.x <= FOREST_WIDTH - PLAYER_SIZE - 40
                and 40 <= next_rect.y <= FOREST_HEIGHT - PLAYER_SIZE - 40
            ):
                if dx != 0 or dy != 0:
                    if frame % 12 == 0 and SOUND_ENABLED:
                        step_sound.play()
                player.rect = next_rect

        elif not in_building and not show_inventory and not show_log:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += speed
            if dx < 0:
                player.facing_left = True
            elif dx > 0:
                player.facing_left = False

            next_rect = player.rect.move(dx, dy)
            if (
                0 <= next_rect.x <= MAP_WIDTH - PLAYER_SIZE
                and 0 <= next_rect.y <= MAP_HEIGHT - PLAYER_SIZE
            ):
                collision = False
                for b in BUILDINGS:
                    overlap = next_rect.clip(b.rect)
                    if overlap.width > 8 and overlap.height > 8:
                        collision = True
                        break
                if not collision:
                    if dx != 0 or dy != 0:
                        if frame % 12 == 0 and SOUND_ENABLED:
                            step_sound.play()
                        player.energy = max(player.energy - 0.04, 0)
                        cost_mult = 1 - 0.05 * player.perk_levels.get("Iron Will", 0)
                        if player.companion == "Cat":
                            cost_mult *= 1 - 0.1 * player.companion_level
                        player.energy = max(player.energy - 0.02 * cost_mult, 0)
                    player.rect = next_rect

        near_building = None
        for b in BUILDINGS:
            if player.rect.colliderect(b.rect):
                near_building = b
                break
        near_npc = None
        for n in NPCS:
            if player.rect.colliderect(n.rect):
                near_npc = n
                break
        if not inside_home and not inside_bar and not inside_forest:
            for b in BUILDINGS:
                if player.rect.colliderect(b.rect):
                    near_building = b
                    break

        if (
            not inside_home
            and not inside_bar
            and not inside_forest
            and not in_building
            and shop_message_timer == 0
            and not show_log
        ):
            location = near_building.btype if near_building else None
            desc = random_event(player, location)
            if desc:
                shop_message = desc
                shop_message_timer = 90
                quest_sound.play()
                if SOUND_ENABLED:
                    quest_sound.play()

        if (
            not inside_home
            and not inside_bar
            and not inside_forest
            and not in_building
            and near_npc
            and not show_inventory
            and not show_log
        ):
            if keys[pygame.K_e]:
                text = "Hi there!"
                if near_npc.quest:
                    state = player.npc_progress.get(near_npc.name)
                    if state is None:
                        text = near_npc.quest.description
                        player.side_quest = near_npc.quest.name
                        player.npc_progress[near_npc.name] = 1
                    elif state == 1 and player.side_quest is None:
                        near_npc.quest.reward(player)
                        player.npc_progress[near_npc.name] = 2
                        text = "Thanks for the help!"
                if near_npc.romanceable:
                    hearts = player.relationships.get(near_npc.name, 0)
                    if player.last_talk.get(near_npc.name) != player.day:
                        hearts = min(MAX_HEARTS, hearts + 1)
                        player.relationships[near_npc.name] = hearts
                        player.last_talk[near_npc.name] = player.day
                        text = f"+1 heart ({hearts}/{MAX_HEARTS})"
                    if hearts >= 8 and near_npc.name not in player.romanced:
                        player.romanced.append(near_npc.name)
                        text = f"You are now dating {near_npc.name}!"
                elif near_npc.quest is None:
                    text = "Good to see you."
                near_npc.bubble_message = text
                near_npc.bubble_timer = 90
                shop_message = f"{near_npc.name}: {text}"
                shop_message_timer = 90
            elif keys[pygame.K_g] and near_npc.romanceable and player.inventory:
                item = player.inventory.pop(0)
                hearts = player.relationships.get(near_npc.name, 0)
                hearts = min(MAX_HEARTS, hearts + 2)
                player.relationships[near_npc.name] = hearts
                player.last_talk[near_npc.name] = player.day
                text = f"Gave {item.name}! ({hearts}/{MAX_HEARTS})"
                if hearts >= 8 and near_npc.name not in player.romanced:
                    player.romanced.append(near_npc.name)
                    text = f"{near_npc.name} is now your partner!"
                near_npc.bubble_message = text
                near_npc.bubble_timer = 90
                shop_message = f"{near_npc.name}: {text}"
                shop_message_timer = 90

        if (
            not inside_home
            and not inside_bar
            and not inside_forest
            and not in_building
            and near_building
            and not show_inventory
            and not show_log
        ):
            if keys[pygame.K_e]:
                if building_open(near_building.btype, player.time, player):
                    in_building = near_building.btype

                    enter_sound.play()
                    if near_building.btype == "home":
                        inside_home = True
                        home_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            DOOR_RECT.x + 10,
                            DOOR_RECT.y + DOOR_RECT.height - PLAYER_SIZE - 10,
                        )
                    elif near_building.btype == "bar":
                        inside_bar = True
                        bar_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            BAR_DOOR_RECT.x + 10,
                            BAR_DOOR_RECT.y + BAR_DOOR_RECT.height - PLAYER_SIZE - 10,
                        )
                    elif near_building.btype == "forest":
                        inside_forest = True
                        forest_return = (player.rect.x, player.rect.y)
                        player.rect.topleft = (
                            FOREST_DOOR_RECT.x + 10,
                            FOREST_DOOR_RECT.y
                            + FOREST_DOOR_RECT.height
                            - PLAYER_SIZE
                            - 10,
                        )
                    else:
                        in_building = near_building.btype
                    if SOUND_ENABLED:
                        enter_sound.play()

                else:
                    shop_message = "Closed right now"
                    shop_message_timer = 60

        if in_building:
            if keys[pygame.K_q]:
                in_building = None

        if player.energy == 0:
            player.health = max(player.health - 0.08, 0)

        cam_x = min(
            max(0, player.rect.centerx - settings.SCREEN_WIDTH // 2),
            MAP_WIDTH - settings.SCREEN_WIDTH,
        )
        cam_y = min(
            max(0, player.rect.centery - settings.SCREEN_HEIGHT // 2),
            MAP_HEIGHT - settings.SCREEN_HEIGHT,
        )
        if inside_home:
            cam_x = cam_y = 0
            draw_home_interior(
                screen,
                font,
                player,
                frame if dx or dy else 0,
                BED_RECT,
                DOOR_RECT,
                compute_furniture_rects(player),
            )
        elif inside_bar:
            cam_x = cam_y = 0
            draw_bar_interior(
                screen,
                font,
                player,
                frame if dx or dy else 0,
                COUNTER_RECT,
                BJ_RECT,
                SLOT_RECT,
                DART_RECT,
                BRAWL_RECT,
                BAR_DOOR_RECT,
            )
        elif inside_forest:
            cam_x = cam_y = 0
            draw_forest_area(
                screen,
                font,
                player,
                frame if dx or dy else 0,
                FOREST_ENEMY_RECTS,
                FOREST_DOOR_RECT,
            )
        else:
            cam_x = min(
                max(0, player.rect.centerx - settings.SCREEN_WIDTH // 2),
                MAP_WIDTH - settings.SCREEN_WIDTH,
            )
            cam_y = min(
                max(0, player.rect.centery - settings.SCREEN_HEIGHT // 2),
                MAP_HEIGHT - settings.SCREEN_HEIGHT,
            )

        draw_sky(screen, player.time)

        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)
        draw_decorations(screen, cam_x, cam_y)

        for b in BUILDINGS:
            draw_rect = b.rect.move(-cam_x, -cam_y)
            draw_building(
                screen,
                Building(draw_rect, b.name, b.btype),
                highlight=(b == near_building),
            )

        for n in NPCS:
            draw_npc(screen, n, font, (-cam_x, -cam_y))

        pr = player.rect.move(-cam_x, -cam_y)
        draw_player_sprite(
            screen,
            pr,
            frame if dx or dy else 0,
            player.facing_left,
            player.color,
            player.head_color,
        )

        target_building = quest_target_building(player, BUILDINGS)
        if target_building:
            draw_quest_marker(screen, pr, target_building.rect, cam_x, cam_y)

        draw_day_night(screen, player.time)
        draw_weather(screen, player.weather)

        draw_ui(screen, font, player, QUESTS, STORY_QUESTS)
        draw_hotkey_bar(screen, font, player, hotkey_rects)
        if show_inventory:
            draw_inventory_screen(
                screen,
                font,
                player,
                slot_rects,
                item_rects,
                (dragging_item, drag_pos) if dragging_item else None,
                hotkey_rects,
                compute_furniture_rects(player) if inside_home else None,
            )
        if show_perk_menu:
            draw_perk_menu(screen, font, player, PERKS)
        if show_log:
            draw_quest_log(screen, font, QUESTS, STORY_QUESTS)
        if show_help:
            draw_help_screen(screen, font)

        info_y = 46
        if near_npc and not in_building:
            msg = "[E] Talk"
            msg_surf = font.render(msg, True, (30, 30, 30))
            bg = pygame.Surface(
                (msg_surf.get_width() + 16, msg_surf.get_height() + 6), pygame.SRCALPHA
            )
            bg.fill((255, 255, 255, 210))
            screen.blit(bg, (10, info_y - 4))
            screen.blit(msg_surf, (18, info_y))
            info_y += 28

        if near_building and not in_building:
            msg = ""
            if near_building.btype == "job":
                pay = job_pay(player, "office")
                msg = f"[E] to Work here (+${pay}, -20 energy)"
            elif near_building.btype == "dealer":
                pay = job_pay(player, "dealer")
                msg = f"[E] to Deal drugs (+${pay}, -20 energy)"
            elif near_building.btype == "clinic":
                pay = job_pay(player, "clinic")
                msg = f"[E] to Work here (+${pay}, -20 energy)  [H] heal for $20"
            elif near_building.btype == "home":
                msg = "[E] to enter home"
            elif near_building.btype == "shop":
                msg = "[E] to shop for items"
            elif near_building.btype == "gym":
                msg = "[E] to train (+1 STR, +5 health, -10 energy, -$10)"
            elif near_building.btype == "library":
                msg = "[E] to study (+1 INT, -5 energy, -$5)"
                msg += "  [P] puzzle"
            elif near_building.btype == "park":
                msg = "[E] to chat (+1 CHA, -5 energy)  [F] fish"
            elif near_building.btype == "bar":
                msg = "[E] to gamble and fight"
                msg += "  [D] darts"
            elif near_building.btype == "dungeon":
                msg = "[E] to fight an enemy"
            elif near_building.btype == "forest":
                msg = "[E] to explore the woods"
            elif near_building.btype == "petshop":
                msg = "[E] to adopt a pet"
            elif near_building.btype == "bank":
                msg = "[E] to visit the bank"
            elif near_building.btype == "townhall":
                msg = "[E] to visit the Town Hall"
            elif near_building.btype == "workshop":
                msg = "[E] to craft gear"
            elif near_building.btype == "farm":
                msg = "[E] to manage crops"
            elif near_building.btype == "business":
                msg = "[E] manage or 1-2 buy"
            elif near_building.btype == "mall":
                msg = "[E] to browse the mall  [C] card duel"
            elif near_building.btype == "beach":
                msg = "[E] to relax"
                msg += "  [D] dig"
            elif near_building.btype == "suburbs":
                msg = "[E] to visit the suburbs"
            elif near_building.btype == "boss":
                msg = "[E] to challenge the boss"
            if msg:
                if not building_open(near_building.btype, player.time, player):
                    msg += " (Closed)"
                msg_surf = font.render(msg, True, (30, 30, 30))
                bg = pygame.Surface(
                    (msg_surf.get_width() + 16, msg_surf.get_height() + 6),
                    pygame.SRCALPHA,
                )
                bg.fill((255, 255, 255, 210))
                screen.blit(bg, (10, info_y - 4))
                screen.blit(msg_surf, (18, info_y))

        if in_building:
            txt = ""
            if in_building == "job":
                pay = job_pay(player, "office")
                txt = f"[E] Work (+${pay})  [Q] Leave"
            elif in_building == "dealer":
                pay = job_pay(player, "dealer")
                txt = f"[E] Deal (+${pay})  [Q] Leave"
            elif in_building == "clinic":
                pay = job_pay(player, "clinic")
                txt = f"[E] Work (+${pay})  H:Heal $20  [Q] Leave"
            elif in_building == "home":
                txt = "[E] Sleep  [1-9] Buy upgrade  [Q] Leave"
            elif in_building == "shop":
                txt = "[0-9] Buy items  [Q] Leave"
            elif in_building == "gym":
                txt = "[E] Train  [Q] Leave"
            elif in_building == "library":
                txt = "[E] Study  [P] Puzzle  [Q] Leave"
            elif in_building == "park":
                txt = "[E] Chat  [F] Fish  [Q] Leave"
            elif in_building == "bank":
                txt = (
                    "[E] Talk  [D] Deposit $10  [W] Withdraw $10  [Q] Leave  "
                    f"Bal:${int(player.bank_balance)}"
                )
            elif in_building == "bar":
                txt = (
                    "[B] Buy token  [J] Blackjack  [S] Slots  [D] Darts  "
                    "[F] Fight  [Q] Leave"
                )
            elif in_building == "dungeon":
                txt = "[E] Fight  [Q] Leave"
            elif in_building == "forest":
                txt = "[E] Fight  [Q] Leave"
            elif in_building == "boss":
                txt = "[E] Fight boss  [Q] Leave"
            elif in_building == "petshop":
                txt = "[1-6] Adopt"
                if player.companion:
                    txt += "  T:Train"
                txt += "  [Q] Leave"
            elif in_building == "workshop":
                txt = "1 Potion 2 Sword 3 Up Wpn 4 Up Arm  [Q] Leave"
            elif in_building == "farm":
                txt = "[P] Plant seed  [H] Harvest  S:Sell  [Q] Leave"
            elif in_building == "business":
                opts = []
                for i, (name, cost, _p) in enumerate(BUSINESSES):
                    status = "Owned" if name in player.businesses else f"${cost}"
                    opts.append(f"{i+1}:{name} {status}")
                txt = " ".join(opts) + "  E:Manage  [Q] Leave"
            elif in_building == "mall":
                txt = "[E] Pick up order  C:Duel  [Q] Leave"
            elif in_building == "beach":
                txt = "[E] Relax/Deliver  D:Dig  [Q] Leave"
            elif in_building == "suburbs":
                txt = "[E] Help locals  [Q] Leave"
            draw_tip_panel(screen, font, f"Inside: {in_building.upper()}   {txt}")
            if in_building == "shop":
                for i, (name, cost, _func) in enumerate(SHOP_ITEMS):
                    item_surf = font.render(
                        f"{(i + 1) % 10}:{name} ${cost}", True, (80, 40, 40)
                    )
                    row = i // 5
                    col = i % 5
                    screen.blit(
                        item_surf,
                        (30 + col * 150, settings.SCREEN_HEIGHT - 60 - row * 24),
                    )
                    screen.blit(
                        item_surf,
                        (30 + col * 200, settings.SCREEN_HEIGHT - 60 - row * 24),
                    )
            elif in_building == "home":
                avail = [u for u in HOME_UPGRADES if u[3] <= player.home_level]
                for i, (name, cost, _d, _req) in enumerate(avail):
                    status = "Owned" if name in player.home_upgrades else f"${cost}"
                    item_surf = font.render(
                        f"{i+1}:{name} {status}", True, (80, 40, 40)
                    )
                    screen.blit(item_surf, (30 + i * 260, settings.SCREEN_HEIGHT - 60))
            elif in_building == "petshop":
                for i, (name, cost, _d) in enumerate(COMPANIONS):
                    item_surf = font.render(f"{i+1}:{name} ${cost}", True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 200, settings.SCREEN_HEIGHT - 60))
            elif in_building == "workshop":
                opts = [
                    ("1:Health Potion (2 herbs)", 1),
                    ("2:Iron Sword (3 metal)", 1),
                    ("3:Upgrade Weapon (2 metal)", 1),
                    ("4:Upgrade Armor (2 cloth)", 1),
                    ("5:Decorations (1 metal,2 cloth)", 2),
                    ("6:Energy Potion (3 herbs)", 2),
                    ("7:Flaming Sword (5 metal,2 herbs)", 3),
                    ("8:Fruit Pie (2 produce)", 3),
                ]
                for i, (txt_opt, req) in enumerate(opts):
                    if player.crafting_level < req:
                        txt_opt += f" [Lv{req}]"
                    item_surf = font.render(txt_opt, True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 300, settings.SCREEN_HEIGHT - 60))
            elif in_building == "farm":
                opts = ["P:Plant (-1 seed)", "H:Harvest", "S:Sell produce"]
                for i, txt_opt in enumerate(opts):
                    item_surf = font.render(txt_opt, True, (80, 40, 40))
                    screen.blit(item_surf, (30 + i * 260, settings.SCREEN_HEIGHT - 60))

        elif inside_bar:
            txt = (
                "Use counter to buy tokens, tables to gamble or throw darts, "
                "ring to fight, door to exit"
            )
            draw_tip_panel(screen, font, txt)
        elif inside_forest:
            txt = "Fight enemies or exit via the door"
            draw_tip_panel(screen, font, txt)
        elif inside_home:
            txt = "Use bed to sleep, door to exit 1-3 Buy upgrade"
            draw_tip_panel(screen, font, txt)

        if shop_message_timer > 0:
            shop_message_timer -= 1
            msg_surf = font.render(shop_message, True, (220, 40, 40))
            bg = pygame.Surface(
                (msg_surf.get_width() + 16, msg_surf.get_height() + 8), pygame.SRCALPHA
            )
            bg.fill((255, 255, 255, 240))
            screen.blit(bg, (10, 90))
            screen.blit(msg_surf, (18, 94))

        for n in NPCS:
            if n.bubble_timer > 0:
                n.bubble_timer -= 1

        if player.health <= 0:
            over = font.render(
                "GAME OVER (You collapsed from exhaustion)", True, (255, 0, 0)
            )
            screen.blit(
                over, (settings.SCREEN_WIDTH // 2 - 240, settings.SCREEN_HEIGHT // 2)
            )
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        if check_quests(player) and SOUND_ENABLED:
            quest_sound.play()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

