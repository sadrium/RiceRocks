import pygame
import spritesheet
import os.path
import math
import random
from pygame.locals import *
from SpriteStripAnim import SpriteStripAnim

WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
started = False

class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        self.lifespan = lifespan if lifespan else float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, 'art', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Error while loading image "%s" %s' % (file, pygame.get_error()))
    return surface.convert_alpha()

def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def load_sound(file):
    file = os.path.join(main_dir, 'audio', file)
    sound = pygame.mixer.Sound(file)
    return sound

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def rot_center(image, angle):
    
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Ship:
    def __init__(self, position, vel, angle, image, info):
        self.position = [position[0], position[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.images = image
        self.image = self.images[0]
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.original = self.image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.rect = self.image.get_rect()
        self.center_pos = [(self.position[0] + self.image_width / 2), (self.position[1] + self.image_height / 2)]
        
    def get_radius(self):
        return self.radius

    def get_position(self):
        return self.position

    def turn(self, direction):
        self.angle_vel = direction

    def move(self, thrust):
        self.thrust = thrust
        if self.thrust:
            ship_thrust_sound.play(-1)
        else:
            ship_thrust_sound.stop()

    def shoot(self):
        global missile_group
        base_missle_speed = 6
        forward = angle_to_vector(math.radians(self.angle))
        vel = [0, 0]
        vel[0] = self.vel[0] + forward[0] * base_missle_speed
        vel[1] = self.vel[1] + -forward[1] * base_missle_speed

        position = [0, 0]
        
        position[0] = self.position[0] + (self.radius + 5 + self.image_width / 2 * forward[0])
        position[1] = self.position[1] + (self.radius + 5 + self.image_height / 2 * -forward[1])

        a_missile = Sprite(position, vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

    def draw(self, screen):
        if self.thrust:
            self.original = self.images[1]
        else:
            self.original = self.images[0]

        screen.blit(self.image, self.position)

    def update(self):
        self.position[0] += self.vel[0]
        self.position[1] += self.vel[1]
        self.center_pos = [(self.position[0] + self.image_width / 2), (self.position[1] + self.image_height / 2)]
        
        c = 0.015
        self.vel[0] *= (1 - c)
        self.vel[1] *= (1 - c)

        if self.position[1] + self.image_height <= self.radius:  
            self.position[1] = self.position[1] % HEIGHT + self.image_height
        if self.position[1] >= HEIGHT:
            self.position[1] = self.position[1] % HEIGHT - self.image_height

        if self.position[0] + self.image_width <= 0:  
            self.position[0] = self.position[0] % WIDTH + self.image_width
        if self.position[0] >= WIDTH:
            self.position[0] = self.position[0] % WIDTH - self.image_width

        forward = angle_to_vector(math.radians(self.angle))
        if self.thrust:
            self.vel[0] += forward[0] * 0.1
            self.vel[1] += -forward[1] * 0.1
        self.angle += self.angle_vel
        self.image = rot_center(self.original, self.angle)

class Sprite:
    def __init__(self, position, vel, ang, ang_vel, image, info, sound=None, strip=None):
        self.position = [position[0], position[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.original = self.image
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.center_pos = [(self.position[0] + self.image_width / 2), (self.position[1] + self.image_height / 2)]
        self.age = 0
        if strip:
            self.strip = strip
            self.strip.iter()
        if sound:
            sound.stop()
            sound.play()

    def get_position(self):
        return self.position

    def get_radius(self):
        return self.radius

    def collide(self, other_object):
        distance = dist(self.center_pos, other_object.center_pos)

        if distance > self.radius + other_object.get_radius():
            return False
        elif distance < self.radius + other_object.get_radius():
            return True

    def draw(self, screen):
        if self.animated:
            self.image = self.strip.next()
            screen.blit(self.image, self.position)
        else:
            screen.blit(self.image, self.position)

    def update(self):
        self.position[0] += self.vel[0]
        self.position[1] += self.vel[1]
        self.age += 1
        self.center_pos = [(self.position[0] + self.image_width / 2), (self.position[1] + self.image_height / 2)]
        
        if self.position[1] + self.image_height <= self.radius:
            self.position[1] = self.position[1] % HEIGHT + self.image_height
        if self.position[1] >= HEIGHT:
            self.position[1] = self.position[1] % HEIGHT - self.image_height

        if self.position[0] + self.image_width <= 0:
            self.position[0] = self.position[0] % WIDTH + self.image_width
        if self.position[0] >= WIDTH:
            self.position[0] = self.position[0] % WIDTH - self.image_width

        self.angle += self.angle_vel
        self.image = rot_center(self.original, self.angle)
        
        if self.age < self.lifespan:
            return False
        else:
            return True

def group_collide(group, other_object):
    
    for elem in set(group):
        if elem.collide(other_object):
            an_explosion = Sprite(elem.get_position(), [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound,
                                  explosion_sheet)
            explosion_group.add(an_explosion)
            group.remove(elem)
            return True
    else:
        return False

def group_group_collide(group1, group2):
    score_add = 0
    for elem in set(group1):
        if group_collide(group2, elem):
            group1.remove(elem)
            score_add += 1
    return score_add

def process_sprite_group(group, screen):
    for elem in set(group):
        elem.draw(screen)
        is_old = elem.update()
        if is_old:
            group.remove(elem)

def score_to_range():
    global score
    if score < 10:
        return 1
    elif score >= 10 and score < 20:
        return 2
    elif score >= 20:
        return 4
    else:
        return 5

def rock_spawner():
    global rock_group, started, my_ship, score
    rang = score_to_range()
    if len(rock_group) < 11 and started:
        vel = [0, 0]
        vel[0] = random.randrange(-(rang), rang + 1)
        vel[1] = random.randrange(-(rang), rang + 1)
        x = random.randrange(0, 800)
        y = random.randrange(0, 600)

        ang = (random.randrange(-5, 11))

        a_rock = Sprite([x, y], vel, 0, ang, asteroid_image, asteroid_info)
        distance = dist(my_ship.get_position(), a_rock.get_position())
        if distance > 100:
            rock_group.add(a_rock)

def restart():
    global rock_group, started
    started = False
    for elem in set(rock_group):
        rock_group.discard(elem)

def click(position):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < position[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < position[1] < (center[1] + size[1] / 2)
    lives = 3
    score = 0
    if (not started) and inwidth and inheight:
        soundtrack.stop()
        soundtrack.play()
        started = True

def main():
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Rice Rocks')

    
    ship_info = ImageInfo([45, 45], [90, 90], 35)
    ship_sheet = spritesheet.spritesheet('art/double_ship.png')
    ship_images = ship_sheet.images_at(((0, 0, 90, 90), (90, 0, 90, 90)), colorkey=(255, 255, 255))

    global explosion_info
    explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
    global explosion_image, explosion_sheet
    explosion_sheet = SpriteStripAnim('art/explosion_alpha.png', (0, 0, 128, 128), 24, (255, 255, 255), True, 2)
    explosion_sheet.iter()
    explosion_image = explosion_sheet.next()

    global splash_info
    splash_info = ImageInfo([200, 150], [400, 300])
    global splash_image
    splash_image = load_image('splash.png')

    global asteroid_info
    asteroid_info = ImageInfo([45, 45], [90, 90], 40)
    global asteroid_image
    asteroid_image = load_image('asteroid_blue.png')

    global missile_info
    missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
    global missile_image
    missile_image = load_image('shot2.png')

    
    global ship_thrust_sound, missile_sound, explosion_sound, soundtrack
    soundtrack = load_sound('music.ogg')
    soundtrack.set_volume(0.5)
    missile_sound = load_sound('shoot.wav')
    ship_thrust_sound = load_sound('thrust.wav')
    ship_thrust_sound.set_volume(0.05)
    explosion_sound = load_sound('explode.wav')
    explosion_sound.set_volume(0.05)

    
    global my_ship
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_images, ship_info)
    global rock_group, missile_group, explosion_group
    explosion_group = set([])
    rock_group = set([])
    missile_group = set([])
    
    debris_info = ImageInfo([320, 240], [640, 480])
    background = load_image('nebula_blue.f2014.png')
    debris_image = load_image('debris2_blue.png')

    fontObj = pygame.font.Font(None, 50)
    white_color = pygame.Color(255, 255, 255)

    clock = pygame.time.Clock()
    pygame.time.set_timer(USEREVENT + 1, 1000)
    
    while 1:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == USEREVENT + 1:
                rock_spawner()
            
            if event.type == KEYDOWN and event.key == K_RIGHT:
                my_ship.turn(-5)
            if event.type == KEYDOWN and event.key == K_LEFT:
                my_ship.turn(5)
            if event.type == KEYDOWN and event.key == K_UP:
                my_ship.move(True)
            if event.type == KEYUP and event.key == K_UP:
                my_ship.move(False)
            if event.type == KEYUP and event.key == K_RIGHT:
                my_ship.turn(0)
            if event.type == KEYUP and event.key == K_LEFT:
                my_ship.turn(0)
            if event.type == KEYUP and event.key == K_ESCAPE:
                return
            if event.type == KEYUP and event.key == K_SPACE:
                my_ship.shoot()
            if event.type == pygame.MOUSEBUTTONUP:
                click(pygame.mouse.get_pos())
        
        my_ship.update()

        global score, lives
        if group_collide(rock_group, my_ship):
            lives -= 1
        score += group_group_collide(missile_group, rock_group)

        global time
        time += 1
        wtime = (time / 4) % WIDTH
        screen.blit(background, (0, 0))
        screen.blit(debris_image, ((wtime - WIDTH / 2) - 320, (HEIGHT / 2) - 240))
        screen.blit(debris_image, ((wtime + WIDTH / 2) - 320, (HEIGHT / 2) - 240))

        my_ship.draw(screen)
        process_sprite_group(missile_group, screen)
        process_sprite_group(explosion_group, screen)
        process_sprite_group(rock_group, screen)

        screen.blit(fontObj.render("Score: %d" % score, True, white_color), (0, 0))
        screen.blit(fontObj.render("Lives: %d" % lives, True, white_color), (620, 0))
        
        if not started:
            screen.blit(splash_image,
                        (WIDTH / 2 - (splash_info.get_size()[0] / 2), HEIGHT / 2 - (splash_info.get_size()[1] / 2)))

        pygame.display.flip()
        if lives == 0:
            restart()

if __name__ == '__main__':
    main()
