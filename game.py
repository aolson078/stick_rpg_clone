import sys
import pygame

from entities import Player, Building
from rendering import (
    draw_player,
    draw_building,
    draw_road_and_sidewalks,
    draw_city_walls,
    draw_day_night,
    draw_ui,
)
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    MAP_WIDTH,
    MAP_HEIGHT,
    PLAYER_SIZE,
    PLAYER_SPEED,
    BG_COLOR,
    MINUTES_PER_FRAME,
)

pygame.init()

BUILDINGS = [
    Building(pygame.Rect(200, 150, 200, 120), "Home", "home"),
    Building(pygame.Rect(600, 300, 180, 240), "Office", "job"),
    Building(pygame.Rect(1100, 700, 300, 100), "Shop", "shop"),
    Building(pygame.Rect(400, 900, 160, 180), "Park", "park"),
    Building(pygame.Rect(900, 450, 220, 160), "Gym", "gym"),
    Building(pygame.Rect(1200, 250, 200, 160), "Library", "library"),
]

OPEN_HOURS = {
    "home": (0, 24),
    "job": (8, 18),
    "shop": (9, 21),
    "gym": (6, 22),
    "library": (8, 20),
    "park": (6, 22),
}


def building_open(btype, minutes):
    start, end = OPEN_HOURS.get(btype, (0, 24))
    hour = (minutes / 60) % 24
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    player = Player(pygame.Rect(MAP_WIDTH // 2, MAP_HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE))
    in_building = None
    shop_message = ""
    shop_message_timer = 0
    frame = 0

    while True:
        frame += 1
        player.time += MINUTES_PER_FRAME
        if player.time >= 1440:
            player.time -= 1440
            player.day += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and in_building:
                if in_building == "job":
                    if player.energy >= 20:
                        player.money += 30
                        player.energy -= 20
                        shop_message = "You worked! +$30, -20 energy"
                    else:
                        shop_message = "Too tired to work!"
                    shop_message_timer = 60
                elif in_building == "home":
                    player.energy = 100
                    player.time = 8 * 60
                    player.day += 1
                    shop_message = "You slept. New day!"
                    shop_message_timer = 60
                elif in_building == "shop":
                    if player.money >= 20 and player.health < 100:
                        player.money -= 20
                        player.health = min(player.health + 30, 100)
                        shop_message = "You bought food! +30 health"
                    elif player.money < 20:
                        shop_message = "Not enough money!"
                    elif player.health == 100:
                        shop_message = "Already full health!"
                    shop_message_timer = 60
                elif in_building == "gym":
                    if player.money >= 10 and player.energy >= 10:
                        player.money -= 10
                        player.energy -= 10
                        player.health = min(player.health + 5, 100)
                        player.strength += 1
                        shop_message = "You worked out! +1 STR, +5 health"
                    elif player.money < 10:
                        shop_message = "Need $10 to train"
                    else:
                        shop_message = "Too tired to train!"
                    shop_message_timer = 60
                elif in_building == "library":
                    if player.money >= 5 and player.energy >= 5:
                        player.money -= 5
                        player.energy -= 5
                        player.intelligence += 1
                        shop_message = "You studied! +1 INT"
                    elif player.money < 5:
                        shop_message = "Need $5 to study"
                    else:
                        shop_message = "Too tired to study!"
                    shop_message_timer = 60
                elif in_building == "park":
                    if player.energy >= 5:
                        player.energy -= 5
                        player.charisma += 1
                        shop_message = "You socialized! +1 CHA"
                    else:
                        shop_message = "Too tired to chat!"
                    shop_message_timer = 60

        dx = dy = 0
        keys = pygame.key.get_pressed()
        if not in_building:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= PLAYER_SPEED
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += PLAYER_SPEED
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= PLAYER_SPEED
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += PLAYER_SPEED

            next_rect = player.rect.move(dx, dy)
            if 0 <= next_rect.x <= MAP_WIDTH - PLAYER_SIZE and 0 <= next_rect.y <= MAP_HEIGHT - PLAYER_SIZE:
                collision = False
                for b in BUILDINGS:
                    overlap = next_rect.clip(b.rect)
                    if overlap.width > 8 and overlap.height > 8:
                        collision = True
                        break
                if not collision:
                    if dx != 0 or dy != 0:
                        player.energy = max(player.energy - 0.04, 0)
                    player.rect = next_rect

        near_building = None
        for b in BUILDINGS:
            if player.rect.colliderect(b.rect):
                near_building = b
                break

        if not in_building and near_building:
            if keys[pygame.K_e]:
                if building_open(near_building.btype, player.time):
                    in_building = near_building.btype
                else:
                    shop_message = "Closed right now"
                    shop_message_timer = 60

        if in_building:
            if keys[pygame.K_q]:
                in_building = None

        if player.energy == 0:
            player.health = max(player.health - 0.08, 0)

        cam_x = min(max(0, player.rect.centerx - SCREEN_WIDTH // 2), MAP_WIDTH - SCREEN_WIDTH)
        cam_y = min(max(0, player.rect.centery - SCREEN_HEIGHT // 2), MAP_HEIGHT - SCREEN_HEIGHT)

        screen.fill(BG_COLOR)

        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)

        for b in BUILDINGS:
            draw_rect = b.rect.move(-cam_x, -cam_y)
            draw_building(screen, Building(draw_rect, b.name, b.btype))

        pr = player.rect.move(-cam_x, -cam_y)
        draw_player(screen, pr, frame if dx or dy else 0)

        draw_day_night(screen, player.time)

        draw_ui(screen, font, player)

        info_y = 46
        if near_building and not in_building:
            msg = ""
            if near_building.btype == "job":
                msg = "[E] to Work here (+$30, -20 energy)"
            elif near_building.btype == "home":
                msg = "[E] to Sleep (restore energy, next day)"
            elif near_building.btype == "shop":
                msg = "[E] to buy food (+30 health, -$20)"
            elif near_building.btype == "gym":
                msg = "[E] to train (+1 STR, +5 health, -10 energy, -$10)"
            elif near_building.btype == "library":
                msg = "[E] to study (+1 INT, -5 energy, -$5)"
            elif near_building.btype == "park":
                msg = "[E] to chat (+1 CHA, -5 energy)"
            if msg:
                if not building_open(near_building.btype, player.time):
                    msg += " (Closed)"
                msg_surf = font.render(msg, True, (30, 30, 30))
                bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 6), pygame.SRCALPHA)
                bg.fill((255, 255, 255, 210))
                screen.blit(bg, (10, info_y - 4))
                screen.blit(msg_surf, (18, info_y))

        if in_building:
            panel = pygame.Surface((SCREEN_WIDTH, 100))
            panel.fill((245, 245, 200))
            screen.blit(panel, (0, SCREEN_HEIGHT - 100))
            txt = ""
            if in_building == "job":
                txt = "[E] Work  [Q] Leave"
            elif in_building == "home":
                txt = "[E] Sleep  [Q] Leave"
            elif in_building == "shop":
                txt = "[E] Buy food  [Q] Leave"
            elif in_building == "gym":
                txt = "[E] Train  [Q] Leave"
            elif in_building == "library":
                txt = "[E] Study  [Q] Leave"
            elif in_building == "park":
                txt = "[E] Chat  [Q] Leave"
            tip_surf = font.render(f"Inside: {in_building.upper()}   {txt}", True, (80, 40, 40))
            screen.blit(tip_surf, (20, SCREEN_HEIGHT - 80))

        if shop_message_timer > 0:
            shop_message_timer -= 1
            msg_surf = font.render(shop_message, True, (220, 40, 40))
            bg = pygame.Surface((msg_surf.get_width() + 16, msg_surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 240))
            screen.blit(bg, (10, 90))
            screen.blit(msg_surf, (18, 94))

        if player.health <= 0:
            over = font.render("GAME OVER (You collapsed from exhaustion)", True, (255, 0, 0))
            screen.blit(over, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
