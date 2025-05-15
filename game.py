import pygame
import sys
import math

# --- Settings ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 1600, 1200

PLAYER_SIZE = 32
PLAYER_COLOR = (40, 40, 40)
PLAYER_HEAD_COLOR = (245, 219, 164)
PLAYER_SPEED = 5

BG_COLOR = (180, 220, 190)
BUILDING_COLOR = (200, 170, 120)
HOME_COLOR = (128, 191, 255)
JOB_COLOR = (240, 221, 110)
SHOP_COLOR = (255, 115, 115)
PARK_COLOR = (100, 200, 140)
ROAD_COLOR = (90, 90, 90)
SIDEWALK_COLOR = (190, 190, 190)
CITY_WALL_COLOR = (120, 100, 70)
WINDOW_COLOR = (220, 240, 255)
DOOR_COLOR = (90, 70, 40)
SHADOW_COLOR = (40, 40, 40, 60)

FONT_COLOR = (30, 30, 30)
UI_BG = (255, 255, 255, 230)

pygame.init()

# --- Buildings (Rect, name, type) ---
BUILDINGS = [
    (pygame.Rect(200, 150, 200, 120), "Home", "home"),
    (pygame.Rect(600, 300, 180, 240), "Office", "job"),
    (pygame.Rect(1100, 700, 300, 100), "Shop", "shop"),
    (pygame.Rect(400, 900, 160, 180), "Park", "park"),
]

def draw_player(surface, rect, frame=0):
    # Draw a drop shadow
    x = rect.x + rect.width // 2
    y = rect.y + rect.height
    shadow = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (40, 40, 40, 80), (0, 0, 40, 14))
    surface.blit(shadow, (x - 20, y - 6))

    # Stick figure
    # Animate arms/legs if moving
    swing = math.sin(frame / 6) * 7 if frame else 0
    # Head
    pygame.draw.circle(surface, PLAYER_HEAD_COLOR, (x, y-24), 10)
    pygame.draw.circle(surface, PLAYER_COLOR, (x, y-24), 10, 2)
    # Body
    pygame.draw.line(surface, PLAYER_COLOR, (x, y-14), (x, y), 3)
    # Arms
    pygame.draw.line(surface, PLAYER_COLOR, (x, y-10), (x-13, y-2+int(swing)), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y-10), (x+13, y-2-int(swing)), 3)
    # Legs
    pygame.draw.line(surface, PLAYER_COLOR, (x, y), (x-9, y+16+int(swing)), 3)
    pygame.draw.line(surface, PLAYER_COLOR, (x, y), (x+9, y+16-int(swing)), 3)

def building_color(btype):
    if btype == "home": return HOME_COLOR
    if btype == "job": return JOB_COLOR
    if btype == "shop": return SHOP_COLOR
    if btype == "park": return PARK_COLOR
    return BUILDING_COLOR

def draw_building(surface, b, name, btype):
    # Base rectangle
    pygame.draw.rect(surface, building_color(btype), b, border_radius=9)
    # Roof
    roof = pygame.Rect(b.x, b.y-14, b.width, 18)
    pygame.draw.rect(surface, (150, 140, 100), roof, border_top_left_radius=9, border_top_right_radius=9)
    # Windows
    if btype != "park":
        for i in range(2, b.width//50):
            wx = b.x + 18 + i*50
            wy = b.y + 28
            pygame.draw.rect(surface, WINDOW_COLOR, (wx, wy, 22, 22), border_radius=4)
        # Door
        dx = b.x + b.width//2 - 18
        dy = b.y + b.height - 38
        pygame.draw.rect(surface, DOOR_COLOR, (dx, dy, 36, 38), border_radius=5)
        # Door knob
        pygame.draw.circle(surface, (220, 210, 120), (dx+32, dy+19), 3)
    # Label
    font = pygame.font.SysFont(None, 28)
    label = font.render(name, True, FONT_COLOR)
    label_bg = pygame.Surface((label.get_width()+12, label.get_height()+4), pygame.SRCALPHA)
    label_bg.fill((255,255,255,230))
    surface.blit(label_bg, (b.x + b.width//2 - label.get_width()//2 - 6, b.y - 32))
    surface.blit(label, (b.x + b.width//2 - label.get_width()//2, b.y - 30))

def draw_road_and_sidewalks(surface, cam_x, cam_y):
    # Simple road in the middle of map horizontally
    road_rect = pygame.Rect(0-cam_x, 470-cam_y, MAP_WIDTH, 60)
    pygame.draw.rect(surface, ROAD_COLOR, road_rect)
    # Sidewalks
    pygame.draw.rect(surface, SIDEWALK_COLOR, (0-cam_x, 460-cam_y, MAP_WIDTH, 10))
    pygame.draw.rect(surface, SIDEWALK_COLOR, (0-cam_x, 530-cam_y, MAP_WIDTH, 10))
    # Lane lines
    for x in range(0, MAP_WIDTH, 80):
        pygame.draw.rect(surface, (230, 220, 100), (x-cam_x, 498-cam_y, 36, 6), border_radius=3)

def draw_city_walls(surface, cam_x, cam_y):
    # Outer walls
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, MAP_WIDTH, 12))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, MAP_HEIGHT-12-cam_y, MAP_WIDTH, 12))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (-cam_x, -cam_y, 12, MAP_HEIGHT))
    pygame.draw.rect(surface, CITY_WALL_COLOR, (MAP_WIDTH-12-cam_x, -cam_y, 12, MAP_HEIGHT))

def draw_ui(surface, font, money, energy, health, day):
    bar = pygame.Surface((SCREEN_WIDTH, 36), pygame.SRCALPHA)
    bar.fill(UI_BG)
    text = font.render(
        f"Money: ${int(money)}   Energy: {int(energy)}   Health: {int(health)}   Day: {day}",
        True, FONT_COLOR
    )
    bar.blit(text, (16, 6))
    surface.blit(bar, (0, 0))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stick RPG Mini (Graphics Upgrade)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    player_rect = pygame.Rect(MAP_WIDTH//2, MAP_HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)
    money = 50
    energy = 100
    health = 100
    day = 1

    in_building = None
    shop_message = ""
    shop_message_timer = 0
    frame = 0

    while True:
        frame += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and in_building:
                if in_building == "job":
                    if energy >= 20:
                        money += 30
                        energy -= 20
                        shop_message = "You worked! +$30, -20 energy"
                    else:
                        shop_message = "Too tired to work!"
                    shop_message_timer = 60
                elif in_building == "home":
                    energy = 100
                    day += 1
                    shop_message = "You slept. New day!"
                    shop_message_timer = 60
                elif in_building == "shop":
                    if money >= 20 and health < 100:
                        money -= 20
                        health = min(health + 30, 100)
                        shop_message = "You bought food! +30 health"
                    elif money < 20:
                        shop_message = "Not enough money!"
                    elif health == 100:
                        shop_message = "Already full health!"
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

            next_rect = player_rect.move(dx, dy)
            if 0 <= next_rect.x <= MAP_WIDTH-PLAYER_SIZE and 0 <= next_rect.y <= MAP_HEIGHT-PLAYER_SIZE:
                collision = False
                for b, _, _ in BUILDINGS:
                    overlap = next_rect.clip(b)
                    if overlap.width > 8 and overlap.height > 8:
                        collision = True
                        break
                if not collision:
                    if dx != 0 or dy != 0:
                        energy = max(energy - 0.04, 0)
                    player_rect = next_rect

        near_building = None
        for b, name, btype in BUILDINGS:
            if player_rect.colliderect(b):
                near_building = (b, name, btype)
                break

        if not in_building and near_building:
            if keys[pygame.K_e]:
                in_building = near_building[2]

        if in_building:
            if keys[pygame.K_q]:
                in_building = None

        if energy == 0:
            health = max(health - 0.08, 0)

        cam_x = min(max(0, player_rect.centerx - SCREEN_WIDTH//2), MAP_WIDTH - SCREEN_WIDTH)
        cam_y = min(max(0, player_rect.centery - SCREEN_HEIGHT//2), MAP_HEIGHT - SCREEN_HEIGHT)

        # --- Draw ---
        screen.fill(BG_COLOR)

        draw_road_and_sidewalks(screen, cam_x, cam_y)
        draw_city_walls(screen, cam_x, cam_y)

        # Draw buildings
        for b, name, btype in BUILDINGS:
            draw_rect = b.move(-cam_x, -cam_y)
            draw_building(screen, draw_rect, name, btype)

        # Draw player hitbox (green box)
        pr = player_rect.move(-cam_x, -cam_y)
        # pygame.draw.rect(screen, (0,255,0), pr, 2) # Uncomment for debug
        draw_player(screen, pr, frame if dx or dy else 0)

        draw_ui(screen, font, money, energy, health, day)

        # --- UI: Building interaction/help ---
        info_y = 46
        if near_building and not in_building:
            _, name, btype = near_building
            msg = ""
            if btype == "job":
                msg = "[E] to Work here (+$30, -20 energy)"
            elif btype == "home":
                msg = "[E] to Sleep (restore energy, next day)"
            elif btype == "shop":
                msg = "[E] to buy food (+30 health, -$20)"
            if msg:
                msg_surf = font.render(msg, True, FONT_COLOR)
                bg = pygame.Surface((msg_surf.get_width()+16, msg_surf.get_height()+6), pygame.SRCALPHA)
                bg.fill((255,255,255,210))
                screen.blit(bg, (10, info_y-4))
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
            tip_surf = font.render(f"Inside: {in_building.upper()}   {txt}", True, (80, 40, 40))
            screen.blit(tip_surf, (20, SCREEN_HEIGHT - 80))

        if shop_message_timer > 0:
            shop_message_timer -= 1
            msg_surf = font.render(shop_message, True, (220, 40, 40))
            bg = pygame.Surface((msg_surf.get_width()+16, msg_surf.get_height()+8), pygame.SRCALPHA)
            bg.fill((255,255,255,240))
            screen.blit(bg, (10, 90))
            screen.blit(msg_surf, (18, 94))

        if health <= 0:
            over = font.render("GAME OVER (You collapsed from exhaustion)", True, (255, 0, 0))
            screen.blit(over, (SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2500)
            return

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
