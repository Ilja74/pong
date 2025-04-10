import pygame
import sys
import random
import time
from collections import deque

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the sound mixer

# Set up the game window
WIDTH = 800
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong by Ilja Liepelt")

# Colors - Higher contrast color palette
LIGHT_GREEN = (0, 255, 0)      # Bright green for paddles and ball
DARK_GREEN = (0, 25, 0)        # Very dark green for background 
GOLD = (255, 215, 0)           # Bright gold for stars and scores

# Game objects
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
BLOCK_SIZE = PADDLE_WIDTH  # Make blocks as thin as paddles

# Sound effects
paddle_hit_sound = pygame.mixer.Sound("snd/paddle_hit.wav")  # Create sound object
boom_sound = pygame.mixer.Sound("snd/boom.mp3")  # Create boom sound for scoring
pygame.mixer.music.load("snd/pong.mp3")  # Load background music
pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
pygame.mixer.music.play(-1)  # Play music in endless loop (-1)

# Star settings
STAR_COUNT = 50
stars = []
for _ in range(STAR_COUNT):
    # Add direction and speed for each star
    stars.append([
        random.randint(0, WIDTH),  # x position
        random.randint(0, HEIGHT), # y position
        random.randint(1, 3),      # size
        random.uniform(-2, 2),     # x speed
        random.uniform(-2, 2)      # y speed
    ])

# Screen shake settings
shake_duration = 0
shake_intensity = 10

# Block settings
blocks = []
last_block_spawn = time.time()
block_visible_duration = 8  # seconds
block_hidden_duration = 10  # seconds
block_phase = "hidden"

# Paddle class
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 8
        self.score = 0

    def move(self, up=True):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        if not up and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(WINDOW, LIGHT_GREEN, self.rect)

# Ball class
class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - BALL_SIZE//2, 
                              HEIGHT//2 - BALL_SIZE//2,
                              BALL_SIZE, BALL_SIZE)
        self.speed_x = 4 * random.choice((1, -1))  # Reduced from 6 to 4
        self.speed_y = 4 * random.choice((1, -1))  # Reduced from 6 to 4
        self.trail = deque(maxlen=10)  # Store last 10 positions

    def move(self):
        # Store current position before moving
        self.trail.append(self.rect.center)
        
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Wall collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def reset(self):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.speed_x *= random.choice((1, -1))
        self.speed_y *= random.choice((1, -1))
        self.trail.clear()  # Clear the trail when ball resets

    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            # Make trail fade out by reducing alpha
            alpha = int(255 * (i / len(self.trail)))
            trail_surface = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*LIGHT_GREEN, alpha), (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)
            WINDOW.blit(trail_surface, (pos[0] - BALL_SIZE//2, pos[1] - BALL_SIZE//2))
        
        # Draw current ball
        pygame.draw.rect(WINDOW, LIGHT_GREEN, self.rect)

# Create game objects
player = Paddle(50, HEIGHT//2 - PADDLE_HEIGHT//2)
opponent = Paddle(WIDTH - 50 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
ball = Ball()

# Game font
font = pygame.font.Font(None, 74)

# Game loop
clock = pygame.time.Clock()

while True:
    current_time = time.time()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Block spawning logic
    if block_phase == "hidden" and current_time - last_block_spawn >= block_hidden_duration:
        blocks = []
        # Spawn 1 or 2 blocks
        num_blocks = random.randint(1, 2)
        for _ in range(num_blocks):
            x = random.randint(WIDTH//4, 3*WIDTH//4 - BLOCK_SIZE)
            y = random.randint(BLOCK_SIZE, HEIGHT - BLOCK_SIZE)
            blocks.append(pygame.Rect(x, y, BLOCK_SIZE, PADDLE_HEIGHT))  # Use PADDLE_HEIGHT for blocks
        block_phase = "visible"
        last_block_spawn = current_time
    elif block_phase == "visible" and current_time - last_block_spawn >= block_visible_duration:
        blocks = []
        block_phase = "hidden"
        last_block_spawn = current_time

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move(up=True)
    if keys[pygame.K_s]:
        player.move(up=False)

    # Simple AI for opponent
    if opponent.rect.centery < ball.rect.centery:
        opponent.move(up=False)
    if opponent.rect.centery > ball.rect.centery:
        opponent.move(up=True)

    # Ball movement
    ball.move()

    # Ball collision with paddles
    if ball.rect.colliderect(player.rect) or ball.rect.colliderect(opponent.rect):
        ball.speed_x *= -1
        paddle_hit_sound.play()  # Play sound when ball hits paddle

    # Ball collision with blocks
    for block in blocks[:]:
        if ball.rect.colliderect(block):
            blocks.remove(block)
            player.score += 1
            ball.reset()
            boom_sound.play()

    # Scoring and screen shake
    if ball.rect.left <= 0:
        opponent.score += 1
        ball.reset()
        shake_duration = 20  # Set shake duration in frames
        boom_sound.play()  # Play boom sound when scoring
    if ball.rect.right >= WIDTH:
        player.score += 1
        ball.reset()
        shake_duration = 20  # Set shake duration in frames
        boom_sound.play()  # Play boom sound when scoring

    # Drawing
    WINDOW.fill(DARK_GREEN)
    
    # Apply screen shake if active
    shake_offset_x = 0
    shake_offset_y = 0
    if shake_duration > 0:
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)
        shake_duration -= 1
    
    # Update and draw stars with shake effect
    for star in stars:
        pygame.draw.circle(WINDOW, GOLD, 
                         (int(star[0] + shake_offset_x), 
                          int(star[1] + shake_offset_y)), star[2])
        
        # Update star positions with smooth movement
        star[0] += star[3]  # Move in x direction
        star[1] += star[4]  # Move in y direction
        
        # Wrap around screen edges
        if star[0] < 0:
            star[0] = WIDTH
            star[3] = random.uniform(-2, 2)
        elif star[0] > WIDTH:
            star[0] = 0
            star[3] = random.uniform(-2, 2)
            
        if star[1] < 0:
            star[1] = HEIGHT
            star[4] = random.uniform(-2, 2)
        elif star[1] > HEIGHT:
            star[1] = 0
            star[4] = random.uniform(-2, 2)
    
    # Draw game objects with shake effect
    temp_surface = pygame.Surface((WIDTH, HEIGHT))
    temp_surface.fill(DARK_GREEN)
    
    # Draw blocks
    for block in blocks:
        pygame.draw.rect(WINDOW, GOLD, block)
    
    player.draw()
    opponent.draw()
    ball.draw()

    # Draw scores
    player_text = font.render(str(player.score), True, GOLD)
    opponent_text = font.render(str(opponent.score), True, GOLD)
    WINDOW.blit(player_text, (WIDTH//4 + shake_offset_x, 20 + shake_offset_y))
    WINDOW.blit(opponent_text, (3*WIDTH//4 + shake_offset_x, 20 + shake_offset_y))

    # Draw center line
    pygame.draw.aaline(WINDOW, LIGHT_GREEN, 
                      (WIDTH//2 + shake_offset_x, shake_offset_y), 
                      (WIDTH//2 + shake_offset_x, HEIGHT + shake_offset_y))

    # Update display
    pygame.display.flip()
    clock.tick(60)
