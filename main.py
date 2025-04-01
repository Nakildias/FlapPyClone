import pygame
import random
import sys
import math
import os

PATH = os.path.abspath('.')+'/'

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 288, 512
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED|pygame.FULLSCREEN)
pygame.display.set_caption('FlapPy Clone')

# Set up the clock
clock = pygame.time.Clock()
FPS = 60

# Load images
bird_images = [pygame.image.load(PATH+'blackbird-upflap.png').convert_alpha(), pygame.image.load(PATH+'blackbird-midflap.png').convert_alpha(), pygame.image.load(PATH+'blackbird-downflap.png').convert_alpha()]
pipe_image = pygame.image.load(PATH+'pipe-green.png').convert_alpha()
base_image = pygame.image.load(PATH+'base.png').convert_alpha()
background_image = pygame.image.load(PATH+'background-day.png').convert_alpha()
game_over_image = pygame.image.load(PATH+'gameover.png').convert_alpha()
message_image = pygame.image.load(PATH+'message.png').convert_alpha()
highscore_image = pygame.image.load(PATH+'highscore.png').convert_alpha()

# Load number images for score display
number_images = {str(i): pygame.image.load(PATH+f'{i}.png').convert_alpha() for i in range(10)}

# Load sounds
wing_sounds = [PATH+'wingflap1.wav', PATH+'wingflap2.wav', PATH+'wingflap3.wav', PATH+'wingflap4.wav']
hit_sound = pygame.mixer.Sound(PATH+'hit.wav')
point_sound = pygame.mixer.Sound(PATH+'point.wav')
gameover_sound = pygame.mixer.Sound(PATH+'gameover.wav')

# Set up the bird
bird_x = 50
bird_y = HEIGHT // 2
bird_velocity = 0
gravity = 0.5
bird_flap_power = -10
bird_animation_index = 0

# Add a variable to control the bobbing speed and amplitude
bobbing_speed = 0.01
bobbing_amplitude = 5  # You can adjust this value to control the height of the bobbing

# Variables for wing flapping animation in waiting for start state
wing_flap_timer = 0  # Timer to control the flap speed
wing_flap_interval = 200  # Interval between wing flaps (in milliseconds)
waiting_flap_index = 0  # To alternate between bird images

# Set up pipes
pipe_width = 50
pipe_gap = 150
pipe_velocity = 3
pipe_list = []

# Set up the base
base1_x = 0
base2_x = base_image.get_width()
base_y = HEIGHT - 50
base_velocity = 3

# Set up the game
score = 0
game_over = False
waiting_for_start = True
bird_rect = pygame.Rect(bird_x, bird_y, bird_images[0].get_width(), bird_images[0].get_height())

# Highscore management
HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return 0
    else:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write("0")
        return 0

def save_high_score(high_score):
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(high_score))

high_score = load_high_score()

def draw_score():
    score_str = str(score)
    total_width = sum(number_images[digit].get_width() for digit in score_str)
    x_offset = (WIDTH - total_width) // 2

    for digit in score_str:
        screen.blit(number_images[digit], (x_offset, 10))
        x_offset += number_images[digit].get_width()

def draw_high_score():
    high_score_str = str(high_score)
    total_width = sum(number_images[digit].get_width() for digit in high_score_str)
    x_offset = (WIDTH - total_width) // 2

    for digit in high_score_str:
        screen.blit(number_images[digit], (x_offset, HEIGHT // 2))
        x_offset += number_images[digit].get_width()

def draw_window():
    global bird_y, wing_flap_timer, waiting_flap_index

    # Apply bobbing effect when waiting for start
    if waiting_for_start:
        bird_y = HEIGHT // 2 + math.sin(pygame.time.get_ticks() * bobbing_speed) * bobbing_amplitude

        # Handle the wing flapping animation in the waiting state
        wing_flap_timer += clock.get_time()  # Increment the timer by the elapsed time (in milliseconds)
        if wing_flap_timer >= wing_flap_interval:
            wing_flap_timer = 0  # Reset the timer
            waiting_flap_index = (waiting_flap_index + 1) % 3  # Cycle through 0, 1, 2 for flapping images

    # Use waiting_flap_index when in waiting state, otherwise, use bird_animation_index
    screen.blit(background_image, (0, 0))

    for pipe in pipe_list:
        screen.blit(pipe_image, (pipe[0], pipe[1]))
        screen.blit(pygame.transform.flip(pipe_image, False, True), (pipe[0], pipe[1] - pipe_gap - pipe_image.get_height()))

    tilt_angle = min(max(-bird_velocity * 3, -30), 30)
    bird_image = bird_images[waiting_flap_index] if waiting_for_start else bird_images[bird_animation_index]
    rotated_bird = pygame.transform.rotate(bird_image, tilt_angle)
    bird_rect_rotated = rotated_bird.get_rect(center=(bird_x + bird_image.get_width() // 2,
                                                       bird_y + bird_image.get_height() // 2))
    screen.blit(rotated_bird, bird_rect_rotated.topleft)

    screen.blit(base_image, (base1_x, base_y))
    screen.blit(base_image, (base2_x, base_y))
    draw_score()

    if waiting_for_start:
        screen.blit(message_image, (WIDTH // 2 - message_image.get_width() // 2, HEIGHT // 6))

    if game_over:
        update_high_score()
        screen.blit(game_over_image, (WIDTH // 2 - game_over_image.get_width() // 2, HEIGHT // 4))
        screen.blit(highscore_image, (WIDTH // 2 - highscore_image.get_width() // 2, HEIGHT // 2.40))
        draw_high_score()

    pygame.display.update()

def update_high_score():
    global high_score
    # Update high score if needed
    if score > high_score:
        high_score = score
        save_high_score(high_score)

def handle_bird_movement():
    global bird_velocity, bird_y, bird_animation_index

    bird_velocity += gravity
    bird_y += bird_velocity
    bird_rect.y = bird_y

    if bird_velocity < -1:
        bird_animation_index = 0
    elif bird_velocity < 1:
        bird_animation_index = 1
    else:
        bird_animation_index = 2

def handle_bird_flap():
    global bird_animation_index

    if pygame.event.get(pygame.USEREVENT):
        bird_animation_index = (bird_animation_index + 1) % 3  # Switch to the next wing image
        if bird_animation_index == 0:  # If we're back to the first image, stop the timer
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop the timer after one cycle


def handle_pipes():
    global score, pipe_list, game_over
    for pipe in pipe_list:
        pipe[0] -= pipe_velocity
        if pipe[0] + pipe_width < 0:
            pipe_list.remove(pipe)
            if not game_over:
                score += 1
                point_sound.play()

    if len(pipe_list) == 0 or pipe_list[-1][0] < WIDTH - 200:
        pipe_height = random.randint(200, 400)
        pipe_list.append([WIDTH, pipe_height])

def check_collisions():
    global game_over
    if bird_y < 0 or bird_y + bird_images[0].get_height() > base_y:
        game_over = True
        hit_sound.play()
        gameover_sound.play()

    for pipe in pipe_list:
        if bird_rect.colliderect(pygame.Rect(pipe[0], pipe[1] - pipe_gap - pipe_image.get_height(), pipe_width, pipe_image.get_height())) or \
           bird_rect.colliderect(pygame.Rect(pipe[0], pipe[1], pipe_width, pipe_image.get_height())):
            game_over = True
            hit_sound.play()
            gameover_sound.play()

def handle_base():
    global base1_x, base2_x
    base1_x -= base_velocity
    base2_x -= base_velocity

    if base1_x <= -base_image.get_width():
        base1_x = base2_x + base_image.get_width()
    if base2_x <= -base_image.get_width():
        base2_x = base1_x + base_image.get_width()

def restart_game():
    global bird_y, bird_velocity, score, pipe_list, game_over, waiting_for_start, bird_rect

    bird_y = HEIGHT // 2
    bird_velocity = 0
    score = 0
    pipe_list.clear()
    pipe_list.append([WIDTH, random.randint(200, 400)])
    game_over = False
    waiting_for_start = True
    bird_rect.y = bird_y

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if waiting_for_start:
                    waiting_for_start = False
                elif not game_over:
                    # Handle bird flap when space is pressed
                    bird_velocity = bird_flap_power
                    wing_sound.play()

                    # Set bird's wing to flapping position (full flap)
                    bird_animation_index = 0  # Start with up flap

                    # Optionally, add a timer or frame counter to allow for mid and down flap:
                    pygame.time.set_timer(pygame.USEREVENT, 100)  # Trigger flap progression
                else:
                    restart_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if waiting_for_start:
                    waiting_for_start = False
                elif not game_over:
                    # Handle bird flap when left mouse button is clicked
                    bird_velocity = bird_flap_power
                    random_sound = random.choice(wing_sounds)
                    wing_sound = pygame.mixer.Sound(random_sound)
                    wing_sound.play()

                    # Set bird's wing to flapping position (full flap)
                    bird_animation_index = 0  # Start with up flap

                    # Optionally, add a timer or frame counter to allow for mid and down flap:
                    pygame.time.set_timer(pygame.USEREVENT, 100)  # Trigger flap progression
                else:
                    restart_game()

    # Ensure the base moves only when the game is running or waiting for start
    if not game_over:
        handle_base()

    if not game_over and not waiting_for_start:
        handle_bird_movement()
        handle_pipes()
        check_collisions()
        handle_bird_flap()  # Make sure to call the flapping handler

    draw_window()
