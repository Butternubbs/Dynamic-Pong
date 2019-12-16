import sys
import math
import random
import pygame

NUM_PADDLES = 5 #works best with at least 5 for single player, 4 for multi player
MULTI = False
UNIQUE_KEYS = [(pygame.K_BACKQUOTE, pygame.K_1),
               (pygame.K_LEFT, pygame.K_RIGHT), (pygame.K_a, pygame.K_d),
               (pygame.K_5, pygame.K_6), (pygame.K_8, pygame.K_9),
               (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET),
               (pygame.K_v, pygame.K_b), (pygame.K_k, pygame.K_l)]

#Single player controls with left & right arrow keys
#Player keys: (Supports up to 8 players)
#1- ~ & 1
#2- left & right arrow keys
#3- a & d
#4- 5 & 6
#5- 8 & 9
#6- left & right brackets
#7- v & b
#8- k & l
#Have fun twisting your fingers in knots!
#Maybe this would work better as an online game...

class Ball(pygame.sprite.Sprite):
    def __init__(self, pos, direction, size, *groups):
        super().__init__(groups)
        self.normspeed = 3 #never set this higher than 1/2 paddle thickness
        self.speed = self.normspeed
        self.angle = direction
        self.image = pygame.Surface(size)
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(topleft = pos)
        self.position = list(self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask.fill()
    def update(self):
        dy = -self.speed*math.sin(self.angle)
        dx = self.speed*math.cos(self.angle)
        self.position[0] += dx
        self.position[1] += dy
        self.rect.center = self.position
        self.speed = self.normspeed #reset increased speed after collision
        for pad in pygame.sprite.spritecollide(self, paddles, False):
            if pygame.sprite.collide_mask(self, pad):
                self.angle = (-(self.angle - 2*pad.angle))%(2*math.pi)
                self.speed *= 2 #move the ball a little extra next frame to ensure that it's no longer colliding with the paddle
                return 1
        return 0
                
class Paddle(pygame.sprite.Sprite):
    def __init__(self, centerpt, length, thickness, angle, color, keys, *groups):
        super().__init__(groups)
        angle += math.pi
        self.image = pygame.Surface((length, length), pygame.SRCALPHA)
        width = int(length * abs(math.cos(angle)))
        height = int(length * abs(math.sin(angle)))
        self.rect = pygame.rect.Rect(centerpt[0] - width/2, centerpt[1] - height/2, width, height)
        self.position = list(self.rect.center)
        if angle%math.pi >= math.pi/2 and angle%math.pi < math.pi:
            pygame.draw.line(self.image, color, (0,0), (width, height), thickness)
        else:
            pygame.draw.line(self.image, color, (0, height), (width, 0), thickness)
        self.speed = 5
        self.angle = angle%(2*math.pi)
        self.mask = pygame.mask.from_surface(self.image)
        self.keys = keys
    def update(self):
        pressed = pygame.key.get_pressed()
        if not MULTI:
            if pressed[pygame.K_LEFT]:
                dy = self.speed*math.sin(self.angle)
                dx = -self.speed*math.cos(self.angle)
                self.position[0] += dx
                self.position[1] += dy
                self.rect.center = self.position
            elif pressed[pygame.K_RIGHT]:
                dy = -self.speed*math.sin(self.angle)
                dx = self.speed*math.cos(self.angle)
                self.position[0] += dx
                self.position[1] += dy
                self.rect.center = self.position
        else:
            if pressed[self.keys[0]]:
                dy = self.speed*math.sin(self.angle)
                dx = -self.speed*math.cos(self.angle)
                self.position[0] += dx
                self.position[1] += dy
                self.rect.center = self.position
            elif pressed[self.keys[1]]:
                dy = -self.speed*math.sin(self.angle)
                dx = self.speed*math.cos(self.angle)
                self.position[0] += dx
                self.position[1] += dy
                self.rect.center = self.position

paddles = pygame.sprite.Group()
pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Pong")
timer = pygame.time.Clock()

def main():
    background = pygame.Surface((600,600))
    pygame.draw.circle(background, (200,50,0), (300,300), 440)
    pygame.draw.circle(background, (160,40,0), (300,300), 400)
    pygame.draw.circle(background, (120,30,0), (300,300), 360)
    pygame.draw.circle(background, (80,20,0), (300,300), 320)
    pygame.draw.circle(background, (40,10,0), (300,300), 280)
    pygame.draw.circle(background, (0,0,0), (300,300), 240)
    ball_timer = 0
    rallies = 0
    for i in range(NUM_PADDLES):
        if i < UNIQUE_KEYS.__len__():
            Paddle([300+250*math.sin(math.pi*i/(NUM_PADDLES/2)), 300+250*math.cos(math.pi*i/(NUM_PADDLES/2))], 100, 10, i*math.pi/(NUM_PADDLES/2), (255 - i*int(255/NUM_PADDLES),0, i*int(255/NUM_PADDLES)), UNIQUE_KEYS[i], paddles)
        else:
            Paddle([300+250*math.sin(math.pi*i/(NUM_PADDLES/2)), 300+250*math.cos(math.pi*i/(NUM_PADDLES/2))], 100, 10, i*math.pi/(NUM_PADDLES/2), (255 - i*int(255/NUM_PADDLES),0, i*int(255/NUM_PADDLES)), UNIQUE_KEYS[0], paddles)
    ball = Ball((300,300), random.random() * math.pi*2, (5, 5))
    paused = False
    while True:
        if not paused:
            screen.fill((0,0,0))
            screen.blit(background, background.get_rect())
            paddles.draw(screen)
            for p in paddles.sprites():
                p.update()
            screen.blit(ball.image,ball.rect)
            pygame.display.flip()
            if ball_timer > 0:
                ball_timer -= 1
            else:
                rallies += ball.update()
            if ball.rect.left > 650 or ball.rect.right < -50 or ball.rect.top > 650 or ball.rect.bottom < -50:
                ball = Ball((300,300), random.random() * math.pi*2, (5, 5))
                ball_timer += 15
                print("Rallies: " + str(rallies))
                rallies = 0
        timer.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    paused = not paused

if __name__ == "__main__":
    main()