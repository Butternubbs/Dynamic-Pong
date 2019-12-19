import sys
import colorsys
import math
import random
import pygame

NUM_PADDLES = 200 #works best with at least 5 for single player, 4 for multi player
AI_PLAYERS = 200 #max seems to be 448 for some reason
MULTI = False

PADDLE_LENGTH = 60
PADDLE_THICKNESS = 10
PADDLE_RADIUS = 250
PADDLE_RESTRICTION = 60 #how far a paddle can move in one direction (scales with speed)
PADDLE_SPEED = 5

BALL_SIZE = 5
BALL_SPEED = 3

SCREEN_SIZE = 600
FPS = 60

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
        self.normspeed = BALL_SPEED #never set this higher than 1/2 paddle thickness
        self.speed = self.normspeed
        self.angle = direction
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=pos)
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
    def __init__(self, centerpt, length, thickness, angle, color, keys, ai, *groups):
        super().__init__(groups)
        self.ai = ai
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
        self.speed = PADDLE_SPEED
        self.angle = angle%(2*math.pi)
        self.mask = pygame.mask.from_surface(self.image)
        self.keys = keys
        self.restriction = 60#int((1/(2*PADDLE_SPEED))*(PADDLE_RADIUS + (PADDLE_LENGTH/2)))
        self.linear_pos = 0
    def update(self, ball):
        dy = self.speed*math.sin(self.angle)
        dx = self.speed*math.cos(self.angle)
        if not self.ai:
            pressed = pygame.key.get_pressed()
            if not MULTI:
                if pressed[pygame.K_RIGHT]:
                    if self.linear_pos < self.restriction:
                        self.position[0] -= dx
                        self.position[1] += dy
                        self.rect.center = self.position
                        self.linear_pos += 1
                elif pressed[pygame.K_LEFT]:
                    if self.linear_pos > -self.restriction:
                        self.position[0] += dx
                        self.position[1] -= dy
                        self.rect.center = self.position
                        self.linear_pos -= 1
            else:
                if pressed[self.keys[0]]:
                    if self.linear_pos < self.restriction:
                        self.position[0] -= dx
                        self.position[1] += dy
                        self.rect.center = self.position
                        self.linear_pos += 1
                elif pressed[self.keys[1]]:
                    if self.linear_pos > -self.restriction:
                        self.position[0] += dx
                        self.position[1] -= dy
                        self.rect.center = self.position
                        self.linear_pos -= 1
        else:
            perp = (self.angle + math.pi/2)%math.pi
            ball_to_pad = math.atan((ball.position[1] - self.position[1])/(ball.position[0] - self.position[0]))
            if ball_to_pad < 0:
                ball_to_pad += math.pi
            ball_to_pad = math.pi - ball_to_pad
            if self.angle > math.pi:
                if self.angle%math.pi >= (math.pi/2):
                    if ball_to_pad <= self.angle%math.pi and ball_to_pad >= perp:
                        if self.linear_pos < self.restriction:
                            self.position[0] += dx
                            self.position[1] -= dy
                            self.rect.center = self.position
                            self.linear_pos += 1
                    else:
                        if self.linear_pos > -self.restriction:
                            self.position[0] -= dx
                            self.position[1] += dy
                            self.rect.center = self.position
                            self.linear_pos -= 1
                else:
                    if ball_to_pad > self.angle%math.pi and ball_to_pad <= perp:
                        if self.linear_pos < self.restriction:
                            self.position[0] -= dx
                            self.position[1] += dy
                            self.rect.center = self.position
                            self.linear_pos += 1
                    else:
                        if self.linear_pos > -self.restriction:
                            self.position[0] += dx
                            self.position[1] -= dy
                            self.rect.center = self.position
                            self.linear_pos -= 1
            else:
                if self.angle%math.pi >= (math.pi/2):
                    if ball_to_pad <= self.angle%math.pi and ball_to_pad >= perp:
                        if self.linear_pos < self.restriction:
                            self.position[0] += dx
                            self.position[1] -= dy
                            self.rect.center = self.position
                            self.linear_pos += 1
                    else:
                        if self.linear_pos > -self.restriction:
                            self.position[0] -= dx
                            self.position[1] += dy
                            self.rect.center = self.position
                            self.linear_pos -= 1
                else:
                    if ball_to_pad > self.angle%math.pi and ball_to_pad <= perp:
                        if self.linear_pos < self.restriction:
                            self.position[0] -= dx
                            self.position[1] += dy
                            self.rect.center = self.position
                            self.linear_pos += 1
                    else:
                        if self.linear_pos > -self.restriction:
                            self.position[0] += dx
                            self.position[1] -= dy
                            self.rect.center = self.position
                            self.linear_pos -= 1

def getColor(x):
    #k = float(1/3)
    #ymax = float(255)
    #xmax = float(NUM_PADDLES) - 1
    #r = max(ymax/(k*xmax)*(abs(x-xmax/2) - xmax * (1/2-k)), 0)#(3/xmax)*255*(abs(i-(xmax/2))) - (255/2)
    #g = max(-ymax/(k*xmax)*(abs(x-k*xmax) - k*xmax), 0)
    #b = max(-ymax/(k*xmax)*(abs(x-(1-k)*xmax) - k*xmax), 0)
    #print(r, g, b)
    return (hsv2rgb((1/NUM_PADDLES)*x,1,1))

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

paddles = pygame.sprite.Group()
timer = pygame.time.Clock()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), pygame.RESIZABLE)
    fullscreen = False
    pygame.display.set_caption("Pong")
    background = pygame.Surface((SCREEN_SIZE,SCREEN_SIZE))
    center = int(SCREEN_SIZE/2)
    pygame.draw.circle(background, (200,50,0), (center,center), int(center * 1.5))
    pygame.draw.circle(background, (160,40,0), (center,center), int(center * 1.35))
    pygame.draw.circle(background, (120,30,0), (center,center), int(center * 1.2))
    pygame.draw.circle(background, (80,20,0), (center,center), int(center * 1.05))
    pygame.draw.circle(background, (40,10,0), (center,center), int(center * 0.9))
    pygame.draw.circle(background, (0,0,0), (center,center), int(center * 0.75))
    ball_timer = 0
    rallies = 0
    for i in range(NUM_PADDLES - AI_PLAYERS):
        if i < UNIQUE_KEYS.__len__():
            Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[i], False, paddles)
        else:
            Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[0], False, paddles)
    for i in range(NUM_PADDLES - AI_PLAYERS, NUM_PADDLES):
        Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[0], True, paddles)
    for i in range(NUM_PADDLES - AI_PLAYERS):
        if i < UNIQUE_KEYS.__len__():
            Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[i], False, paddles)
        else:
            Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[0], False, paddles)
    for i in range(NUM_PADDLES - AI_PLAYERS, NUM_PADDLES):
        Paddle([center+PADDLE_RADIUS*math.sin(math.pi*i/(NUM_PADDLES/2)), center+PADDLE_RADIUS*math.cos(math.pi*i/(NUM_PADDLES/2))], PADDLE_LENGTH, PADDLE_THICKNESS, i*math.pi/(NUM_PADDLES/2), getColor(i), UNIQUE_KEYS[0], True, paddles)
    ball = Ball((center,center), random.random() * math.pi*2, (BALL_SIZE, BALL_SIZE))
    paused = False
    while True:
        if not paused:
            screen.fill((0,0,0))
            screen.blit(background, background.get_rect())
            paddles.draw(screen)
            for p in paddles.sprites():
                p.update(ball)
            screen.blit(ball.image,ball.rect)
            pygame.display.flip()
            if ball_timer > 0:
                ball_timer -= 1
            else:
                rallies += ball.update()
            if ball.rect.left > SCREEN_SIZE+50 or ball.rect.right < -50 or ball.rect.top > SCREEN_SIZE+50 or ball.rect.bottom < -50:
                ball = Ball((center,center), random.random() * math.pi*2, (BALL_SIZE, BALL_SIZE))
                ball_timer += 25
                print("Rallies: " + str(rallies))
                rallies = 0
        timer.tick(FPS)
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
                if event.key == pygame.K_LSHIFT:
                    if not fullscreen:
                        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), pygame.FULLSCREEN)
                        fullscreen = True
                    else:
                        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), pygame.RESIZABLE)
                        fullscreen = False

if __name__ == "__main__":
    main()
