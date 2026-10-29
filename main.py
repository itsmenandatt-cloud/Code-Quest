
import pygame
import random
import math

pygame.init()

# หน้าต่างเกม
WIDTH, HEIGHT = 900, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Code Quest")
clock = pygame.time.Clock()

# สี
WHITE = (245, 245, 245)
BLACK = (25, 25, 35)
BLUE = (65, 130, 230)
RED = (220, 65, 65)
GREEN = (60, 190, 100)
YELLOW = (255, 205, 65)
GRAY = (100, 100, 115)
PURPLE = (155, 85, 220)
ORANGE = (240, 140, 40)

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 64)

# ตัวละคร
player = pygame.Rect(100, 350, 44, 60)
enemy = pygame.Rect(740, 350, 44, 60)

player_hp = 100
enemy_hp = 100
player_speed = 5
player_facing = 1

# ระบบกระโดด
player_y = float(player.y)
player_velocity_y = 0
GRAVITY = 0.7
JUMP_POWER = -13
is_jumping = False

# คูลดาวน์ของผู้เล่น (มิลลิวินาที)
ATTACK_COOLDOWN = 1000
SKILL_COOLDOWN = 10000

last_attack = -ATTACK_COOLDOWN
last_skill = -SKILL_COOLDOWN

# สถานะศัตรู
ENEMY_ACTIVE_TIME = 15000
ENEMY_TIRED_TIME = 5000
SWORD_WINDUP = 1500
SWORD_COOLDOWN = 2000

enemy_phase = "active"
phase_started = pygame.time.get_ticks()
next_enemy_action = 0

# สถานะการโจมตีของศัตรู
enemy_action = "idle"
sword_hit_time = 0

# ปืนยิง 10 นัด
BURST_SHOTS = 10
SHOT_INTERVAL = 600
shots_remaining = 0
next_shot_time = 0
bullet_speed = 5

projectiles = []

# ข้อความบนหน้าจอ
message = "A/D: Move | Left Click: Attack | Right Click: Skill | Space: Jump"
message_until = 0

game_over = False
result = ""

def show_message(text, duration=1200):
    global message, message_until
    message = text
    message_until = pygame.time.get_ticks() + duration

def draw_hp(x, y, hp, label):
    pygame.draw.rect(screen, GRAY, (x, y, 200, 22))

    color = GREEN if hp > 60 else YELLOW if hp > 30 else RED
    bar_width = int(200 * max(0, hp) / 100)

    pygame.draw.rect(screen, color, (x, y, bar_width, 22))
    pygame.draw.rect(screen, BLACK, (x, y, 200, 22), 2)

    text = font.render(f"{label}: {max(0, hp)}", True, BLACK)
    screen.blit(text, (x, y - 28))

def distance_between(a, b):
    return abs(a.centerx - b.centerx)

def player_attack(now, skill=False):
    global enemy_hp, last_attack, last_skill

    if skill:
        if now - last_skill < SKILL_COOLDOWN:
            show_message("Skill is recharging!")
            return

        if distance_between(player, enemy) > 150:
            show_message("Too far away!")
            last_skill = now
            return

        enemy_hp = max(0, enemy_hp - 15)
        last_skill = now
        show_message("Special Skill! -15 HP")

    else:
        if now - last_attack < ATTACK_COOLDOWN:
            show_message("Attack is recharging!")
            return

        if distance_between(player, enemy) > 100:
            show_message("Too far away!")
            last_attack = now
            return

        enemy_hp = max(0, enemy_hp - 5)
        last_attack = now
        show_message("Sword Attack! -5 HP")

def fire_bullet(now):
    global shots_remaining, next_shot_time

    start_x = enemy.centerx
    start_y = enemy.centery

    dx = player.centerx - start_x
    dy = player.centery - start_y
    length = math.hypot(dx, dy) or 1

    vx = dx / length * bullet_speed
    vy = dy / length * bullet_speed

    bullet = pygame.Rect(start_x, start_y, 14, 14)

    projectiles.append({
        "rect": bullet,
        "vx": vx,
        "vy": vy
    })

    shots_remaining -= 1
    next_shot_time = now + SHOT_INTERVAL

def start_gun_attack(now):
    global enemy_action, shots_remaining, next_shot_time

    enemy_action = "gun_warning"
    shots_remaining = BURST_SHOTS
    next_shot_time = now + 2000

    show_message("WARNING! ENEMY GUN ATTACK!", 1000)

def reset_game():
    global player_hp, enemy_hp, player_facing
    global last_attack, last_skill
    global enemy_phase, phase_started, next_enemy_action
    global enemy_action, sword_hit_time
    global shots_remaining, next_shot_time
    global projectiles, game_over, result
    global player_y, player_velocity_y, is_jumping

    player.x, player.y = 100, 350
    player_y = float(player.y)
    player_velocity_y = 0
    is_jumping = False
    enemy.x, enemy.y = 740, 350

    player_hp = 100
    enemy_hp = 100
    player_facing = 1

    last_attack = -ATTACK_COOLDOWN
    last_skill = -SKILL_COOLDOWN

    enemy_phase = "active"
    phase_started = pygame.time.get_ticks()
    next_enemy_action = phase_started

    enemy_action = "idle"
    sword_hit_time = 0

    shots_remaining = 0
    next_shot_time = 0
    projectiles = []

    game_over = False
    result = ""

running = True

while running:
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping:
                    player_velocity_y = JUMP_POWER
                    is_jumping = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player_attack(now)
                elif event.button == 3:
                    player_attack(now, skill=True)

    if not game_over:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.x -= player_speed
            player_facing = -1

        if keys[pygame.K_d]:
            player.x += player_speed
            player_facing = 1

        player.x = max(0, min(player.x, WIDTH - player.width))

        # ระบบกระโดดและแรงโน้มถ่วง
        if is_jumping:
            player_velocity_y += GRAVITY
            player_y += player_velocity_y
            player.y = round(player_y)

            if player.y >= 350:
                player.y = 350
                player_y = float(player.y)
                player_velocity_y = 0
                is_jumping = False

        # สลับช่วงต่อสู้กับช่วงเหนื่อย
        elapsed = now - phase_started

        if enemy_phase == "active" and elapsed >= ENEMY_ACTIVE_TIME:
            enemy_phase = "tired"
            phase_started = now
            enemy_action = "idle"
            shots_remaining = 0
            projectiles.clear()
            show_message("Enemy is exhausted!", ENEMY_TIRED_TIME)

        elif enemy_phase == "tired" and elapsed >= ENEMY_TIRED_TIME:
            enemy_phase = "active"
            phase_started = now
            next_enemy_action = now
            enemy_action = "idle"
            show_message("Enemy is back!", 1200)

        # ศัตรูเลือกโจมตีแบบสุ่มในช่วงต่อสู้
        if enemy_phase == "active":

            if enemy_action == "idle" and now >= next_enemy_action:
                close_enough = distance_between(player, enemy) <= 120

                # ใช้ดาบเมื่ออยู่ใกล้และสุ่มเลือกดาบ
                if close_enough and random.random() < 0.5:
                    enemy_action = "sword_windup"
                    sword_hit_time = now + SWORD_WINDUP
                    show_message("WARNING! ENEMY HEAVY ATTACK!", 1500)

                else:
                    start_gun_attack(now)

            # ดาบง้าง 1.5 วินาทีก่อนฟัน
            if enemy_action == "sword_windup" and now >= sword_hit_time:
                if distance_between(player, enemy) <= 145:
                    player_hp = max(0, player_hp - 30)
                    show_message("Heavy Sword Hit! -30 HP")
                else:
                    show_message("You dodged the sword!", 1000)

                enemy_action = "idle"
                next_enemy_action = now + SWORD_COOLDOWN

            # เตือนก่อนยิง แล้วค่อยยิง 10 นัด
            if enemy_action == "gun_warning" and now >= next_shot_time:
                enemy_action = "gun_burst"
                fire_bullet(now)

            elif enemy_action == "gun_burst":
                if shots_remaining > 0 and now >= next_shot_time:
                    fire_bullet(now)

                if shots_remaining <= 0:
                    enemy_action = "idle"
                    next_enemy_action = now + SWORD_COOLDOWN

        # อัปเดตกระสุนและตรวจสอบการชน
        for shot in projectiles[:]:
            shot["rect"].x += round(shot["vx"])
            shot["rect"].y += round(shot["vy"])

            if shot["rect"].colliderect(player):
                player_hp = max(0, player_hp - 10)
                show_message("Gun Hit! -10 HP", 700)
                projectiles.remove(shot)

            elif not screen.get_rect().colliderect(shot["rect"]):
                projectiles.remove(shot)

        # ตรวจสอบผลแพ้ชนะ
        if enemy_hp <= 0:
            game_over = True
            result = "YOU WIN!"

        elif player_hp <= 0:
            game_over = True
            result = "GAME OVER"

    # วาดฉาก
    screen.fill(WHITE)
    pygame.draw.rect(screen, (220, 215, 200), (0, 410, WIDTH, 140))
    pygame.draw.line(screen, BLACK, (0, 410), (WIDTH, 410), 3)

    # วาดผู้เล่น
    pygame.draw.rect(screen, BLUE, player)
    pygame.draw.rect(screen, BLACK, (player.x + 8, player.y + 10, 8, 8))
    pygame.draw.rect(screen, BLACK, (player.x + 28, player.y + 10, 8, 8))

    # วาดศัตรู
    enemy_color = GRAY if enemy_phase == "tired" else RED
    pygame.draw.rect(screen, enemy_color, enemy)
    pygame.draw.rect(screen, BLACK, (enemy.x + 8, enemy.y + 10, 8, 8))
    pygame.draw.rect(screen, BLACK, (enemy.x + 28, enemy.y + 10, 8, 8))

    # ดาบผู้เล่น
    sword_x = player.right if player_facing == 1 else player.left - 24
    pygame.draw.rect(screen, GRAY, (sword_x, player.y + 28, 24, 5))

    # แสดงสถานะการโจมตีของศัตรู
    if enemy_action == "sword_windup":
        warning = font.render("HEAVY ATTACK!", True, RED)
        screen.blit(warning, warning.get_rect(center=(enemy.centerx, enemy.y - 25)))

    elif enemy_action == "gun_warning":
        warning = font.render("GUN WARNING!", True, ORANGE)
        screen.blit(warning, warning.get_rect(center=(enemy.centerx, enemy.y - 25)))

    # วาดกระสุน
    for shot in projectiles:
        pygame.draw.ellipse(screen, PURPLE, shot["rect"])

    # หลอด HP
    draw_hp(30, 55, player_hp, "PLAYER")
    draw_hp(WIDTH - 230, 55, enemy_hp, "ENEMY")

    # แสดงคูลดาวน์สกิล
    skill_elapsed = now - last_skill

    if skill_elapsed >= SKILL_COOLDOWN:
        skill_text = "Skill (Right Click): READY"
        skill_color = GREEN
    else:
        skill_seconds = (SKILL_COOLDOWN - skill_elapsed + 999) // 1000
        skill_text = f"Skill (Right Click): {skill_seconds}s"
        skill_color = RED

    skill_surface = font.render(skill_text, True, skill_color)
    screen.blit(skill_surface, (30, HEIGHT - 32))

    # แสดงช่วงของศัตรู
    if enemy_phase == "active":
        phase_text = "ENEMY: FIGHTING"
        remaining = max(0, (ENEMY_ACTIVE_TIME - (now - phase_started)) // 1000)
    else:
        phase_text = "ENEMY: EXHAUSTED"
        remaining = max(0, (ENEMY_TIRED_TIME - (now - phase_started)) // 1000)

    phase_surface = font.render(
        f"{phase_text} ({remaining}s)",
        True,
        RED if enemy_phase == "active" else GRAY
    )
    screen.blit(phase_surface, phase_surface.get_rect(center=(WIDTH // 2, 25)))

    if now < message_until:
        msg = font.render(message, True, BLACK)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 100)))

     # หน้าจอจบเกม
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 190))
        screen.blit(overlay, (0, 0))

        result_text = big_font.render(
            result, True, GREEN if enemy_hp <= 0 else RED
        )
        screen.blit(
            result_text,
            result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        )

        restart_text = font.render("Press R to Restart", True, BLACK)
        screen.blit(
            restart_text,
            restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
