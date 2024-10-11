import pygame, random, windowcaptions
from sys import exit

pygame.init()
clock = pygame.time.Clock()

# The Window
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption(random.choice(windowcaptions.captionlist()))

# Images
bird_images = [pygame.image.load("assets/bird_fly0.png"),
               pygame.image.load("assets/bird_fly1.png"),
               pygame.image.load("assets/bird_fly2.png"),]

skyline_image = pygame.image.load("assets/background.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")

# Game variables
scroll_speed = 5
bird_start_position = 100,250
score = 0
font = pygame.font.SysFont('Bahnschrift', 40)
stopped = True

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.vel = 0
        self.hop = False
        self.alive = True

    def update(self, user_input):
        # Bird animation (There is only one frame )
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        # The hop
        self.vel += 0.5
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.hop = False

        self.image = pygame.transform.rotate(self.image, self.vel * -2)

        # Da user input
        if user_input[pygame.K_SPACE] and not self.hop and self.rect.y > 0 and self.alive:
            self.hop = True
            self.vel = -7

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # Pipe movement
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

        # Score
        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        # The ground moving
        self.rect.x -= scroll_speed
        if self.rect.right <= 0:
            self.rect.x += self.rect.width * 2

def quit_game():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def main():
    global score

    # Music
    pygame.mixer.init()
    pygame.mixer.music.load("song.wav")
    pygame.mixer.music.play(loops=-1)


    # Instantiate Bird
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    # Pipe setup
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # Instantiate Ground
    x_pos_ground, y_pos_ground = 0,520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    run = True
    while run:

        # Quit
        quit_game()

        # Reset frame
        window.fill((0,0,0))

        # Da user input
        user_input = pygame.key.get_pressed()

        # Drawing the Background
        window.blit(skyline_image, (0, 0))

        # Ground Spawn
        if len(ground) <= 2:
            ground.add(Ground(win_width, y_pos_ground))

        # DRAWING \ Pipes, Ground and Bird
        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        # Draw Score
        score_text = font.render('Score: ' + str(score), True, pygame.Color(2, 48, 32))
        window.blit(score_text, (20, 20))

        # UPDATING \ Pipes, Ground and Bird
        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)

        # Collision Detection [RESTARTING DOES NOT WORK]
        collision_pipes = pygame.sprite.spritecollide(bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            bird.sprite.alive = False
            pygame.mixer.music.stop()
            if collision_ground:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                              win_height // 2 - game_over_image.get_height() // 2))
                if user_input[pygame.K_r]:
                    score = 0
                    break

        # Pipe Spawn
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            y_bottom = y_top + random.randint(90, 130) + bottom_pipe_image.get_height()
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint(180, 250)
        pipe_timer -= 1

        clock.tick(60)
        pygame.display.update()

def menu():
    global stopped

    while stopped:
        quit_game()

        # Drawing the Menu
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, Ground(0, 520))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))

        # Da user input
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()

        pygame.display.update()

menu()