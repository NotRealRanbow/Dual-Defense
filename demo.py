# Import modules
import pygame
from time import time
from random import randint

# Set up the game
pygame.init()
screen = pygame.display.set_mode((600, 500))
pygame.display.set_caption("Cooperative Tower Defense")
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

# Initial parameters
cash = 100
wave = 1
health = 100
selected_tower = None

# Towers & enemies
tower_stats = { # Damage, range, attack_speed
    "warrior": (5, 125, 0.5),
    "mage   ": (4, 200, 0.6),
    "evolved warrior": (7, 130, 0.3),
    "evolved mage": (5, 300, 0.3),
    "haunt": (2, 125, 1)

}
tower_displays = {
    "warrior": (font.render(f"Damage: 5", False, (200, 200, 200)), 
                font.render(f"Range: 125", False, (200, 200, 200)),
                font.render(f"Speed: 0.5", False, (200, 200, 200))
                ),
    "mage   ": (font.render(f"Damage: 4", False, (200, 200, 200)), 
                font.render(f"Range: 200", False, (200, 200, 200)),
                font.render(f"Speed: 0.6", False, (200, 200, 200))
                ),
    "haunt": (font.render(f"Damage: 2", False, (200, 200, 200)), 
                font.render(f"Range: 125", False, (200, 200, 200)),
                font.render(f"Speed: 1", False, (200, 200, 200))
                )
}

selection_to_tower = {
    "warrior_select": "warrior", 
    "mage_select": "mage   ",
    "haunt_select": "haunt"
}

tower_to_evolve = {
    "warrior": "evolved warrior",
    "mage   ": "evolved mage"
}

towers = {} # (x, y) --> last_attack, tower_type
enemies = []

# Text displays
waves_text = font.render(f'Wave: {wave}', False, (0, 0, 0))
health_text = font.render(f'Health: {health}', False, (0, 0, 0))
cash_text = font.render(f'Cash: {cash}', False, (0, 0, 0))

stats_header = font.render(f"Stats:", False, (0, 0, 0))
info_header = font.render(f"Info:", False, (0, 0, 0))

# Image loading
images = {}
def load_images(reference, path, scale):
    images[reference] = pygame.image.load(f"Images/{path}").convert_alpha() 
    images[reference] = pygame.transform.scale(images[reference], (scale, scale))

load_images("track  ", "Middle.png", 100)
load_images("grass  ", "Grass.png", 100)
load_images("flowers", "Flowers.png", 100)
load_images("warrior", "Warrior.png", 100)
load_images("mage   ", "Mage.png", 100)
load_images("enemy1", "Enemy1.png", 100)
load_images("enemy2", "Enemy2.png", 100)
load_images("enemy3", "Enemy3.png", 100)
load_images("gate   ", "Gate.png", 100)
load_images("evolved warrior", "Evolved Warrior.png", 100)
load_images("evolved mage", "Evolved Mage.png", 100)
load_images("haunt", "Haunt.png", 100)


# Map
def draw_map():
    for x in range(5):
        for y in range(5):
            if track[y][x] in tower_stats:
                screen.blit(images["grass  "], (x*100, y*100))
                screen.blit(images[track[y][x]], (x*100, y*100))
            else:
                screen.blit(images[track[y][x]], (x*100, y*100))

track = [
    ["grass  ", "track  ", "grass  ", "flowers", "grass  ", None],
    ["grass  ", "track  ", "track  ", "track  ", "flowers", "warrior_select"],
    ["flowers", "grass  ", "flowers", "track  ", "grass  ", "mage_select"],
    ["grass  ", "grass  ", "grass  ", "track  ", "grass  ", "haunt_select"],
    ["grass  ", "flowers", "grass  ", "gate   ", "flowers", None]
]

# Clocks
clock = pygame.time.Clock()
enemy_clock = time()
wave_clock = time()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x, mouse_y = int(mouse_x/100), int(mouse_y/100)
            
            # Select/unselect tower to place
            if track[mouse_y][mouse_x] in ("warrior_select", "mage_select", "haunt_select"):
                if selected_tower == selection_to_tower[track[mouse_y][mouse_x]]:
                    selected_tower = None
                else:
                    selected_tower = selection_to_tower[track[mouse_y][mouse_x]]

            # Place tower
            elif (track[mouse_y][mouse_x] in ("grass  ", "flowers")) and (selected_tower in tower_stats) and (cash >= 100):
                track[mouse_y][mouse_x] = selected_tower
                towers[(mouse_x, mouse_y, selected_tower)] = time()
                cash -= 100
                cash_text = font.render(f'Cash: {cash}', False, (0, 0, 0))
                selected_tower = None
            
            # Move tower
            elif (track[mouse_y][mouse_x] in tower_stats) and (selected_tower is None) and (cash >= 50):
                selected_tower = track[mouse_y][mouse_x]
                track[mouse_y][mouse_x] = "grass  "
                cash -= 50
                del towers[(mouse_x, mouse_y, selected_tower)]
                cash_text = font.render(f'Cash: {cash}', False, (0, 0, 0))

            # Merge tower
            elif (track[mouse_y][mouse_x] in ("warrior", "mage   ")) and (selected_tower in ("warrior", "mage   ")) and (cash >= 100):
                track[mouse_y][mouse_x] = tower_to_evolve[selected_tower]
                towers[(mouse_x, mouse_y, track[mouse_y][mouse_x])] = time()
                selected_tower = None
                cash -= 100
                cash_text = font.render(f'Cash: {cash}', False, (0, 0, 0))


    # Screen fill
    screen.fill((254, 186, 47))

    # Draw map & menu section
    draw_map()
    screen.blit(images["warrior"], (500, 100))
    screen.blit(images["mage   "], (500, 200))
    screen.blit(images["haunt"], (500, 300))

    # Enemy spawning
    if time() - enemy_clock >= 3*(0.9**(wave-1)):
        enemy_clock = time()
        enemy = randint(1, 3)
        if enemy == 1:
            enemies.append([100, 0, 5*(1.07**(wave-1)), "down", False, "enemy1", 10+int(wave/100)*10, False]) # x, y, health, direction, killed, enemy_type, speed, stunned
        elif enemy == 2:
            enemies.append([100, 0, 4*(1.05**(wave-1)), "down", False, "enemy2", 20+int(wave/100)*10, False]) # x, y, health, direction, killed, enemy_type, speed, stunned
        elif enemy == 3:
            enemies.append([100, 0, 15*(1.05**(wave-1)), "down", False, "enemy3", 5+int(wave/100)*10, False]) # x, y, health, direction, killed, enemy_type, speed, stunned
    
    temp = enemies.copy()
    for i in range(len(temp)):
        for j in towers:
            # Tower damage
            if (time() - towers[j] >= tower_stats[j[2]][2]) and ((temp[i][0] - j[0]*100)**2 + (temp[i][1] - j[1]*100)**2 <= tower_stats[j[2]][1]**2):
                towers[j] = time()
                temp[i][2] -= tower_stats[j[2]][0]
                # Enemy has no more helth
                if (temp[i][2] <= 0) and not(temp[i][4]):
                    enemies.pop(i)
                    temp[i][4] = True
                    cash += 20
                    cash_text = font.render(f'Cash: {cash}', False, (0, 0, 0))
                # Applying stun if the tower was haunt
                if j[2] == "haunt":
                    temp[i][7] = time()
        # Direction
        if temp[i][1] == 100:
            temp[i][3] = "right"
        if temp[i][0] == 300:
            temp[i][3] = "down"
        # Movement
        if not(temp[i][7]) or (time() - temp[i][7] >= 0.5):
            temp[i][7] = False
            if temp[i][3] == "down":
                temp[i][1] += temp[i][6]
            else:
                temp[i][0] += temp[i][6] 
        # End of map
        if temp[i][1] >= 400:
            health -= temp[i][6]
            health_text = font.render(f'Health: {health}', False, (0, 0, 0))
            enemies.pop(i)
        screen.blit(images[temp[i][5]], (temp[i][0], temp[i][1]))

    # Display information
    screen.blit(waves_text, (500, 0))
    screen.blit(health_text, (500, 20))
    screen.blit(cash_text, (500, 40))

    # # Tower rotation
    # for j in range(len(towers)):
    #     max_location = (0, 0)
    #     for i in range(len(enemies)):
    #         if (temp[i][0] - towers[j][0])**2 + (temp[i][1] - towers[j][1])**2 <= towers[j][3]**2 and ((temp[i][1] > max_location[1]) or ((temp[i][0] > max_location[0]) and (temp[i][1] == max_location[1]))):
    #             max_location = (temp[i][0], temp[i][1])
    #     towers[j][6] = atan((temp[i][1] - towers[j][1])/(temp[i][0] - towers[j][0])) * 180/pi + 45
            
    # Darken & show stats
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x, mouse_y = int(mouse_x/100), int(mouse_y/100)
    if track[mouse_y][mouse_x] in ("warrior_select", "mage_select", "haunt_select"):
        darken = pygame.Surface((100,100))
        darken.set_alpha(128)
        darken.fill((0, 0, 0))
        screen.blit(darken, (mouse_x*100, mouse_y*100))
        screen.blit(tower_displays[selection_to_tower[track[mouse_y][mouse_x]]][0], (mouse_x*100, mouse_y*100))
        screen.blit(tower_displays[selection_to_tower[track[mouse_y][mouse_x]]][1], (mouse_x*100, mouse_y*100+20))
        screen.blit(tower_displays[selection_to_tower[track[mouse_y][mouse_x]]][2], (mouse_x*100, mouse_y*100+40))
    
    # Stats when hovering over towers
    elif track[mouse_y][mouse_x] in tower_stats:
        radius = tower_stats[track[mouse_y][mouse_x]][1]
        circle = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)   
        pygame.draw.circle(circle, (0, 0, 0, 128), (radius, radius), radius)
        screen.blit(circle, (mouse_x*100-radius+50, mouse_y*100-radius+50))

        damage_text = font.render(f"Damage: {tower_stats[track[mouse_y][mouse_x]][0]}", False, (0, 0, 0))
        screen.blit(damage_text, (500, 420))
        range_text = font.render(f"Range: {tower_stats[track[mouse_y][mouse_x]][1]}", False, (0, 0, 0))
        screen.blit(range_text, (500, 440))
        speed_text = font.render(f"Speed: {tower_stats[track[mouse_y][mouse_x]][2]}", False, (0, 0, 0))
        screen.blit(speed_text, (500, 460))
        if track[mouse_y][mouse_x] == "haunt":
            debuff_text = font.render(f"Stuns!", False, (0, 0, 0))
            screen.blit(debuff_text, (500, 480))

    # Tower follows cursor
    if selected_tower in ("warrior", "mage   ", "haunt"):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(images[selected_tower], (mouse_x-50, mouse_y-50))
        radius = tower_stats[selected_tower][1]
        circle = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)   
        pygame.draw.circle(circle, (0, 0, 0, 128), (radius, radius), radius)
        screen.blit(circle, (mouse_x-radius, mouse_y-radius))
    
    # Game ends when there is no more health
    if health <= 0:
        while True:     
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

    # Continue with wave
    if time() - wave_clock >= 5:
        wave_clock = time()
        waves_text = font.render(f'Wave: {wave}', False, (0, 0, 0))
        wave += 1

    # Update the display
    clock.tick(30)
    pygame.display.flip()