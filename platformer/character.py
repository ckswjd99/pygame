from setting import *
import pygame, pygame.gfxdraw, numpy
import environment as envi
import entity
import effect
import poly as polygon
from topology import *
from util import *

whole = []


#---------- INFO CONTAINING CLASS ----------#
class basic_stat:
    def __init__(self, acc, jump_power, max_speed, max_hp, max_mp):
        self.acc = acc
        self.jump_power = jump_power
        self.max_speed = max_speed
        self.max_hp = max_hp
        self.max_mp = max_mp

class physics_stat:
    def __init__(self, width, height, air_drag):
        self.width = width
        self.height = height
        self.air_drag = air_drag


#---------- PRIMITIVE CLASS ----------#
class character:
    def __init__(self, name, pos, b_stat, ph_stat):
        self.name = name
        self.pos = list(pos)
        self.speed = [0,0]
        self.acc_ext = [0,0]
        self.b_stat = b_stat
        self.hp = b_stat.max_hp
        self.mp = b_stat.max_mp
        self.ph_stat = ph_stat
        self.harms = []

        self.controlled = { # Value means ticks left
            'rooted': 0,
            'stunned': 0,
            'airborne': 0,
            'exhaust': 0,
            'blinded': 0
            }
        self.disorder_tick = {
            'poisoned': 0,
            'burning': 0
        }
        self.disorder_amount = {
            'poisoned': 0,
            'burning': 0
        }

        whole.append(self)

        self.footprint_delay = 3
        self.footprint_tick = self.footprint_delay

    def replace(self, pos):
        self.pos = list(pos)

    def damaged(self, damage):
        self.harms.append(damage)

    def dead(self):
        pass


#---------- CHILDREN CLASS: PLAYER ----------#
class player(character):
    def __init__(self, name, pos, b_stat, ph_stat):
        character.__init__(self, name, pos, b_stat, ph_stat)
        self.keyset = {'UP':119, 'LEFT':97, 'DOWN':115, 'RIGHT':100}
        self.keydown = {'UP':False, 'LEFT':False, 'DOWN':False, 'RIGHT':False}
        self.poly = pygame.Rect(self.pos[0], self.pos[1], self.ph_stat.width, self.ph_stat.height)
        self.image = pygame.image.load("img/character/player.png")
    
    def update(self):

        #-- MOVEMENT ------------------------------------------------------------------------------#

        # SELF ACCELERATION
        accel = [0,0]
        if self.keydown['UP'] == True:
            accel[1] -= self.b_stat.acc
        if self.keydown['LEFT'] == True:
            accel[0] -= self.b_stat.acc
        if self.keydown['DOWN'] == True:
            accel[1] += self.b_stat.acc
        if self.keydown['RIGHT'] == True:
            accel[0] += self.b_stat.acc
        
        if (-1)*self.b_stat.max_speed <= self.speed[0] + accel[0] and self.speed[0] + accel[0] <= self.b_stat.max_speed:
            self.speed[0] += accel[0]
        elif self.speed[0] + accel[0] > self.b_stat.max_speed and self.speed[0] < self.b_stat.max_speed:
            self.speed[0] = self.b_stat.max_speed
        elif self.speed[0] + accel[0] < (-1)*self.b_stat.max_speed and self.speed[0] > (-1)*self.b_stat.max_speed:
            self.speed[0] = (-1)*self.b_stat.max_speed
            
        if (-1)*self.b_stat.max_speed <= self.speed[1] + accel[1] and self.speed[1] + accel[1] <= self.b_stat.max_speed:
            self.speed[1] += accel[1]
        elif self.speed[1] + accel[1] > self.b_stat.max_speed and self.speed[1] < self.b_stat.max_speed:
            self.speed[1] = self.b_stat.max_speed
        elif self.speed[1] + accel[1] < (-1)*self.b_stat.max_speed and self.speed[1] > (-1)*self.b_stat.max_speed:
            self.speed[1] = (-1)*self.b_stat.max_speed
            
        # GRAVITY
        self.speed[0] += envi.gravity[0]
        self.speed[1] += envi.gravity[1]
        
        # EXTERNAL ACCELERATION
        self.speed[0] += self.acc_ext[0]
        self.speed[1] += self.acc_ext[1]

        # POSITION UPDATE
        for i in range(numpy.abs(self.speed[0])):
            if self.speed[0] > 0:
                self.pos[0] += 1
            else:
                self.pos[0] -= 1
            self.poly = pygame.Rect(self.pos[0], self.pos[1], self.ph_stat.width, self.ph_stat.height)

            # CHECK AVAILABILITY HERE
            collide = False
            for g in entity.wall_whole:
                if self.poly.colliderect(g.poly) == True:
                    collide = True
            if collide == True:
                if self.speed[0] > 0:
                    self.pos[0] -= 1
                else:
                    self.pos[0] += 1
                self.poly = pygame.Rect(self.pos[0], self.pos[1], self.ph_stat.width, self.ph_stat.height)
                break
        
        for i in range(numpy.abs(self.speed[1])):
            if self.speed[1] > 0:
                self.pos[1] += 1
            else:
                self.pos[1] -= 1
            self.poly = pygame.Rect(self.pos[0], self.pos[1], self.ph_stat.width, self.ph_stat.height)

            # CHECK AVAILABILITY HERE
            collide = False
            for g in entity.wall_whole:
                if self.poly.colliderect(g.poly) == True:
                    collide = True
            if collide == True:
                if self.speed[1] > 0:
                    self.pos[1] -= 1
                else:
                    self.pos[1] += 1
                self.poly = pygame.Rect(self.pos[0], self.pos[1], self.ph_stat.width, self.ph_stat.height)
                break

        # AIR DRAG FORCE
        self.speed[0] = int(self.speed[0] * (1-self.ph_stat.air_drag))
        self.speed[1] = int(self.speed[1] * (1-self.ph_stat.air_drag))
        
        #-- \MOVEMENT ------------------------------------------------------------------------------#



        #-- HARMS ------------------------------------------------------------------------------#
        
        for h in self.harms:
            self.hp -= h.amount
            self.harms.remove(h)
        if self.hp <= 0:
            self.dead()

        #-- \HARMS ------------------------------------------------------------------------------#
        
    def render(self):
        #pygame.gfxdraw.rectangle(screen, self.poly, WHITE)
        screen.blit(self.image, (self.pos[0] + camera_offset[0], self.pos[1] + camera_offset[1]))
        
        # FOOTPRINT: NOT SO COOL, SO NOT USING
        #if self.footprint_tick == 0:
        #    effect.spark_gravity_rectangle((self.pos[0]+self.ph_stat.width/2, self.pos[1]+self.ph_stat.height*2/3), self.footprint_delay*2, (0,1), 3, 5, WHITE, 5)
        #    self.footprint_tick = self.footprint_delay
        #else:
        #    self.footprint_tick -= 1
        
            
            
            
#---------- TEST BENCH ----------#
def render():
    screen.fill(BLACK)
    for c in whole:
        c.render()
    for g in entity.wall_whole:
        g.render()

def update():
    for c in whole:
        c.update()
    
    render()

if __name__ == "__main__":
    
    player_bstat = basic_stat(acc=3, jump_power=10, max_speed=10, hp=100)
    player_phstat = physics_stat(width=30, height=40, air_drag=0.2)
    player = player("1P", (500,400), player_bstat, player_phstat)

    entity.wall((2,2))
    
    clock = pygame.time.Clock()

    done = False
    
    while not done:
        
        clock.tick(30)  # 게임의 화면 투사를 30Hz로 설정

        # 이벤트 입력받기
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            if event.type == pygame.KEYDOWN:
                if event.key == player.keyset['UP']:  # key 'w'
                    player.keydown['UP'] = True
                elif event.key == player.keyset['LEFT']:  # key 'a'
                    player.keydown['LEFT'] = True
                elif event.key == player.keyset['DOWN']:  # key 's'
                    player.keydown['DOWN'] = True
                elif event.key == player.keyset['RIGHT']:  # key 'd'
                    player.keydown['RIGHT'] = True
            if event.type == pygame.KEYUP:
                if event.key == player.keyset['UP']:  # key 'w'
                    player.keydown['UP'] = False
                elif event.key == player.keyset['LEFT']:  # key 'a'
                    player.keydown['LEFT'] = False
                elif event.key == player.keyset['DOWN']:  # key 's'
                    player.keydown['DOWN'] = False
                elif event.key == player.keyset['RIGHT']:  # key 'd'
                    player.keydown['RIGHT'] = False

        update()  # call update funtion

        pygame.display.flip()
            
            
            
            
            