import pygame
import math
import random
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robotics LiDAR SLAM & Autonomous Mapping Simulation")
clock = pygame.time.Clock()

# Couleurs (Thème Cyber / Robotique)
DARK_BG = (12, 15, 22)
ROBOT_COLOR = (0, 255, 157)      # Vert néon pour le robot
LIDAR_COLOR = (0, 210, 255, 60)   # Cyan semi-transparent pour les rayons
MAP_POINT_COLOR = (180, 80, 255) # Violet pour la carte reconstruite (SLAM)
OBSTACLE_COLOR = (50, 65, 85)   # Obstacles réels (gris-bleu)
WHITE = (255, 255, 255)
GRAY = (120, 130, 150)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 15)

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0
        self.radius = 14
        self.lidar_range = 180
        self.num_rays = 36  # Balayage 360° avec 36 rayons (1 tous les 10°)

    def move(self, keys):
        # Contrôle manuel avec les flèches du clavier
        if keys[pygame.K_LEFT]:
            self.angle -= 0.05
        if keys[pygame.K_RIGHT]:
            self.angle += 0.05
        if keys[pygame.K_UP]:
            self.speed = min(3.5, self.speed + 0.2)
        elif keys[pygame.K_DOWN]:
            self.speed = max(-2.0, self.speed - 0.2)
        else:
            self.speed *= 0.9  # Freinage naturel

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Bords de l'écran
        self.x = max(30, min(WIDTH - 30, self.x))
        self.y = max(80, min(HEIGHT - 30, self.y))

    def scan(self, obstacles_surface, map_points):
        # Balayage LiDAR 360 degrés
        scan_hits = []
        for i in range(self.num_rays):
            ray_angle = self.angle + (i * 2 * math.pi / self.num_rays)
            hit = False
            
            for d in range(10, self.lidar_range, 4):
                rx = int(self.x + math.cos(ray_angle) * d)
                ry = int(self.y + math.sin(ray_angle) * d)

                if not (0 <= rx < WIDTH and 0 <= ry < HEIGHT):
                    break

                # Si le rayon touche un obstacle
                col = obstacles_surface.get_at((rx, ry))
                if col[0] > 40 and col[1] > 50:
                    scan_hits.append((rx, ry))
                    # Ajouter le point détecté dans la carte SLAM (avec réduction des doublons)
                    grid_key = (rx // 6, ry // 6)
                    map_points[grid_key] = (rx, ry)
                    hit = True
                    break
            
            if not hit:
                end_x = int(self.x + math.cos(ray_angle) * self.lidar_range)
                end_y = int(self.y + math.sin(ray_angle) * self.lidar_range)
                scan_hits.append((end_x, end_y))

        return scan_hits

    def draw(self, surface):
        # Corps du robot
        pygame.draw.circle(surface, ROBOT_COLOR, (int(self.x), int(self.y)), self.radius)
        # Indicateur de direction (Flèche/Proue)
        dir_x = self.x + math.cos(self.angle) * (self.radius + 6)
        dir_y = self.y + math.sin(self.angle) * (self.radius + 6)
        pygame.draw.line(surface, WHITE, (self.x, self.y), (dir_x, dir_y), 3)

# --- GÉNÉRATION D'UNE CARTE D'OBSTACLES RÉELS ---
def create_environment():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((12, 15, 22))

    # Obstacles rectangulaires et circulaires
    pygame.draw.rect(surf, OBSTACLE_COLOR, (180, 140, 150, 180), border_radius=12)
    pygame.draw.rect(surf, OBSTACLE_COLOR, (520, 200, 220, 100), border_radius=12)
    pygame.draw.rect(surf, OBSTACLE_COLOR, (350, 420, 180, 130), border_radius=12)
    pygame.draw.circle(surf, OBSTACLE_COLOR, (750, 480), 65)
    pygame.draw.circle(surf, OBSTACLE_COLOR, (120, 480), 55)

    return surf

env_surface = create_environment()
robot = Robot(WIDTH // 2, HEIGHT // 2)
map_points = {}  # Stocke la carte découverte par le SLAM {(gx, gy): (x, y)}

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Réinitialiser la carte SLAM et la position
                robot = Robot(WIDTH // 2, HEIGHT // 2)
                map_points = {}

    # Déplacement du robot
    robot.move(keys)

    # Scanner avec le LiDAR et construire le SLAM
    scan_hits = robot.scan(env_surface, map_points)

    # --- RENDU GRAPHIQUE ---
    screen.fill(DARK_BG)

    # 1. Dessiner les obstacles réels du monde
    screen.blit(env_surface, (0, 0))

    # 2. Dessiner la carte reconstruite par SLAM (Points découverts)
    for p in map_points.values():
        pygame.draw.circle(screen, MAP_POINT_COLOR, p, 2)

    # 3. Dessiner les faisceaux LiDAR instantanés
    for hx, hy in scan_hits:
        pygame.draw.line(screen, (0, 210, 255), (int(robot.x), int(robot.y)), (hx, hy), 1)
        pygame.draw.circle(screen, WHITE, (hx, hy), 2)

    # 4. Dessiner le robot
    robot.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("ROBOTICS LiDAR SLAM — MAPPING & CARTOGRAPHIE", True, WHITE)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Points explorés dans la carte : {len(map_points)}", True, MAP_POINT_COLOR)
    screen.blit(stats_txt, (35, 45))

    inst_txt = font_small.render("FLÈCHES : Piloter le robot | R : Réinitialiser la carte explorée", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 35, 45))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()