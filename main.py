import pygame
import sys
import random

GREEN_BG = (34, 139, 34)
ROAD_COLOR = (44, 53, 57)
WHITE = (255, 255, 255)
RED_COLOR = (255, 0, 0)
YELLOW_BOX = (255, 215, 0)
PANEL_COLOR = (253, 219, 213)
BOX_GREEN = (0, 255, 0)
LIGHT_RED = (255, 0, 0)
LIGHT_GREEN = (0, 255, 0)
LIGHT_OFF = (50, 50, 50)

CAR_COLORS = [
    (0, 191, 255),    
    (255, 127, 80),   
    (255, 105, 180),  
    (255, 215, 0)     
]

pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic - Simulation style vidéo")
clock = pygame.time.Clock()

ROAD_WIDTH = 160
horizontal_road = pygame.Rect(0, HEIGHT//2 - ROAD_WIDTH//2, WIDTH, ROAD_WIDTH)
vertical_road = pygame.Rect(WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, HEIGHT)
intersection_box = pygame.Rect(WIDTH//2 - ROAD_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2, ROAD_WIDTH, ROAD_WIDTH)

lane_offset = ROAD_WIDTH // 4
font = pygame.font.SysFont("Arial", 22, bold=True)
car_label_font = pygame.font.SysFont("Arial", 12, bold=True)

class Car:
    def __init__(self, direction):
        self.direction = direction
        self.color = random.choice(CAR_COLORS)
        self.speed = 3.0
        self.original_speed = self.speed
        self.is_waiting = False
        
        if direction == "horizontal_right":
            self.lane = random.choice([2, 3])  
            self.width = 45
            self.height = 25
            self.x = -self.width
            self.y = HEIGHT // 2 - ROAD_WIDTH // 2 + (self.lane * lane_offset) + (lane_offset // 2) - (self.height // 2)
        elif direction == "horizontal_left":
            self.lane = random.choice([0, 1])  
            self.width = 45
            self.height = 25
            self.x = WIDTH
            self.y = HEIGHT // 2 - ROAD_WIDTH // 2 + (self.lane * lane_offset) + (lane_offset // 2) - (self.height // 2)
        elif direction == "vertical_down":
            self.lane = random.choice([0, 1])  
            self.width = 25
            self.height = 45
            self.x = WIDTH // 2 - ROAD_WIDTH // 2 + (self.lane * lane_offset) + (lane_offset // 2) - (self.width // 2)
            self.y = -self.height
        elif direction == "vertical_up":
            self.lane = random.choice([2, 3])  
            self.width = 25
            self.height = 45
            self.x = WIDTH // 2 - ROAD_WIDTH // 2 + (self.lane * lane_offset) + (lane_offset // 2) - (self.width // 2)
            self.y = HEIGHT

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_behavior(self, h_signal, v_signal, cars_list):
        stop_line_hr = WIDTH // 2 - ROAD_WIDTH // 2 - 25
        stop_line_hl = WIDTH // 2 + ROAD_WIDTH // 2 + 25
        stop_line_vd = HEIGHT // 2 - ROAD_WIDTH // 2 - 25
        stop_line_vu = HEIGHT // 2 + ROAD_WIDTH // 2 + 25

        self.is_waiting = False
        my_rect = self.get_rect()

        for other_car in cars_list:
            if other_car == self:
                continue
            if self.direction == other_car.direction and self.lane == other_car.lane:
                if self.direction == "horizontal_right" and 0 < other_car.x - (self.x + self.width) < 65:
                    self.speed = 0
                    self.is_waiting = True
                    return
                elif self.direction == "horizontal_left" and 0 < self.x - (other_car.x + other_car.width) < 65:
                    self.speed = 0
                    self.is_waiting = True
                    return
                elif self.direction == "vertical_down" and 0 < other_car.y - (self.y + self.height) < 65:
                    self.speed = 0
                    self.is_waiting = True
                    return
                elif self.direction == "vertical_up" and 0 < self.y - (other_car.y + other_car.height) < 65:
                    self.speed = 0
                    self.is_waiting = True
                    return

        is_near_intersection = False
        if self.direction == "horizontal_right" and stop_line_hr - 40 < self.x + self.width <= stop_line_hr:
            is_near_intersection = True
        elif self.direction == "horizontal_left" and stop_line_hl <= self.x < stop_line_hl + 40:
            is_near_intersection = True
        elif self.direction == "vertical_down" and stop_line_vd - 40 < self.y + self.height <= stop_line_vd:
            is_near_intersection = True
        elif self.direction == "vertical_up" and stop_line_vu <= self.y < stop_line_vu + 40:
            is_near_intersection = True

        if is_near_intersection:
            for other_car in cars_list:
                if other_car == self:
                    continue
                if intersection_box.colliderect(other_car.get_rect()):
                    if (self.direction in ["horizontal_right", "horizontal_left"] and other_car.direction in ["vertical_down", "vertical_up"]) or \
                       (self.direction in ["vertical_down", "vertical_up"] and other_car.direction in ["horizontal_right", "horizontal_left"]):
                        self.speed = 0
                        self.is_waiting = True
                        return

        if self.direction == "horizontal_right":
            if h_signal == "HORIZONTAL_RED" and self.x + self.width <= stop_line_hr and self.x + self.width + self.original_speed > stop_line_hr:
                self.speed = 0
                self.is_waiting = True
            else:
                self.speed = self.original_speed

        elif self.direction == "horizontal_left":
            if h_signal == "HORIZONTAL_RED" and self.x >= stop_line_hl and self.x - self.original_speed < stop_line_hl:
                self.speed = 0
                self.is_waiting = True
            else:
                self.speed = self.original_speed

        elif self.direction == "vertical_down":
            if v_signal == "VERTICAL_RED" and self.y + self.height <= stop_line_vd and self.y + self.height + self.original_speed > stop_line_vd:
                self.speed = 0
                self.is_waiting = True
            else:
                self.speed = self.original_speed

        elif self.direction == "vertical_up":
            if v_signal == "VERTICAL_RED" and self.y >= stop_line_vu and self.y - self.original_speed < stop_line_vu:
                self.speed = 0
                self.is_waiting = True
            else:
                self.speed = self.original_speed

    def move(self):
        self.x += 0 if self.speed == 0 else (self.speed if self.direction == "horizontal_right" else (-self.speed if self.direction == "horizontal_left" else 0))
        self.y += 0 if self.speed == 0 else (self.speed if self.direction == "vertical_down" else (-self.speed if self.direction == "vertical_up" else 0))

    def draw(self, surface):
        car_rect = self.get_rect()
        pygame.draw.rect(surface, self.color, car_rect)
        
        box_rect = pygame.Rect(self.x - 3, self.y - 3, self.width + 6, self.height + 6)
        pygame.draw.rect(surface, BOX_GREEN, box_rect, 1)
        
        label_surface = car_label_font.render("car", True, BOX_GREEN)
        surface.blit(label_surface, (self.x, self.y - 15))

    def is_offscreen(self):
        return self.x < -100 or self.x > WIDTH + 100 or self.y < -100 or self.y > HEIGHT + 100

def draw_traffic_light(surface, x, y, active_color):
    pygame.draw.rect(surface, (15, 15, 15), (x, y, 35, 70), border_radius=8)
    red_color = LIGHT_RED if active_color == "RED" else LIGHT_OFF
    green_color = LIGHT_GREEN if active_color == "GREEN" else LIGHT_OFF
    pygame.draw.circle(surface, red_color, (x + 17, y + 20), 12)
    pygame.draw.circle(surface, green_color, (x + 17, y + 50), 12)

def is_spawn_clear(direction, lane, cars_list):
    for car in cars_list:
        if car.direction == direction and car.lane == lane:
            if direction == "horizontal_right" and car.x < 80:
                return False
            elif direction == "horizontal_left" and car.x > WIDTH - 80:
                return False
            elif direction == "vertical_down" and car.y < 80:
                return False
            elif direction == "vertical_up" and car.y > HEIGHT - 80:
                return False
    return True

cars = []
spawn_timer = 0
light_timer = 0
current_light_state = "VERTICAL_GREEN"

while True:
    dt = clock.tick(60)
    spawn_timer += dt
    light_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if light_timer >= 5000:
        if current_light_state == "VERTICAL_GREEN":
            current_light_state = "HORIZONTAL_GREEN"
        else:
            current_light_state = "VERTICAL_GREEN"
        light_timer = 0

    if spawn_timer >= 450:
        directions = ["horizontal_right", "horizontal_left", "vertical_down", "vertical_up"]
        chosen_dir = random.choice(directions)
        
        if chosen_dir == "horizontal_right":
            chosen_lane = random.choice([2, 3])
        elif chosen_dir == "horizontal_left":
            chosen_lane = random.choice([0, 1])
        elif chosen_dir == "vertical_down":
            chosen_lane = random.choice([0, 1])
        elif chosen_dir == "vertical_up":
            chosen_lane = random.choice([2, 3])
        
        if is_spawn_clear(chosen_dir, chosen_lane, cars):
            cars.append(Car(chosen_dir))
        spawn_timer = 0

    screen.fill(GREEN_BG)
    pygame.draw.rect(screen, ROAD_COLOR, horizontal_road)
    pygame.draw.rect(screen, ROAD_COLOR, vertical_road)
    pygame.draw.rect(screen, YELLOW_BOX, intersection_box, 3)
    
    pygame.draw.line(screen, RED_COLOR, (WIDTH//2 - ROAD_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2), (WIDTH//2 + ROAD_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2), 4)
    pygame.draw.line(screen, RED_COLOR, (WIDTH//2 - ROAD_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2), (WIDTH//2 + ROAD_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2), 4)
    pygame.draw.line(screen, RED_COLOR, (WIDTH//2 - ROAD_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2), (WIDTH//2 - ROAD_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2), 4)
    pygame.draw.line(screen, RED_COLOR, (WIDTH//2 + ROAD_WIDTH//2, HEIGHT//2 - ROAD_WIDTH//2), (WIDTH//2 + ROAD_WIDTH//2, HEIGHT//2 + ROAD_WIDTH//2), 4)

    for i in range(1, 4):
        pygame.draw.line(screen, WHITE, (0, HEIGHT//2 - ROAD_WIDTH//2 + i*lane_offset), (WIDTH, HEIGHT//2 - ROAD_WIDTH//2 + i*lane_offset), 2)
        pygame.draw.line(screen, WHITE, (WIDTH//2 - ROAD_WIDTH//2 + i*lane_offset, 0), (WIDTH//2 - ROAD_WIDTH//2 + i*lane_offset, HEIGHT), 2)

    v_light = "GREEN" if current_light_state == "VERTICAL_GREEN" else "RED"
    h_light = "GREEN" if current_light_state == "HORIZONTAL_GREEN" else "RED"

    draw_traffic_light(screen, WIDTH//2 - ROAD_WIDTH//2 - 45, HEIGHT//2 + ROAD_WIDTH//2 + 10, h_light) 
    draw_traffic_light(screen, WIDTH//2 + ROAD_WIDTH//2 + 10, HEIGHT//2 - ROAD_WIDTH//2 - 80, h_light) 
    draw_traffic_light(screen, WIDTH//2 - ROAD_WIDTH//2 - 45, HEIGHT//2 - ROAD_WIDTH//2 - 80, v_light) 
    draw_traffic_light(screen, WIDTH//2 + ROAD_WIDTH//2 + 10, HEIGHT//2 + ROAD_WIDTH//2 + 10, v_light) 

    h_signal = "HORIZONTAL_GREEN" if current_light_state == "HORIZONTAL_GREEN" else "HORIZONTAL_RED"
    v_signal = "VERTICAL_GREEN" if current_light_state == "VERTICAL_GREEN" else "VERTICAL_RED"

    waiting_count = 0
    for car in cars[:]:
        car.update_behavior(h_signal, v_signal, cars)
        
        if car.is_waiting:
            waiting_count += 1
            
        car.move()
        car.draw(screen)
        if car.is_offscreen():
            cars.remove(car)

    panel_rect = pygame.Rect(30, 30, 320, 180)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=10)
    
    active_cars_count = len(cars)
    is_congested = "OUI" if waiting_count > 5 else "NON"
    avg_wait = waiting_count * 0.35

    stats = [
        f"Vehicules detectes : {active_cars_count}",
        f"Vehicules en attente : {waiting_count}",
        f"Temps attente moyen : {avg_wait:.2f} s",
        f"Congestion : {is_congested}",
        f"Feu actif : {current_light_state}"
    ]
    
    for i, text in enumerate(stats):
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (45, 45 + i * 30))

    pygame.display.update()