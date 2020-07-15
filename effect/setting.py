import pygame

#-- 1. initialize pygame --#
pygame.init()

# 2. 기본 환경 세팅
## Frames per Second
FPS = 30
## COLORS FOR USE
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)

YELLOW= (255, 212,   0)
ORANGE= (255, 127,   0)

# WINDOW SETTING
size   = [1000, 800]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Hello Game")
