import pygame
from pygame.locals import *
from vector import Vector
from arrow import Arrow
from render import CardRenderer,SCREEN_W,SCREEN_H
from cards import *
from state import GameState
from ui import StartGame,BattleIdle,Paused,TitleScreen,CardReward
from enemy import Beholder

testEnemies = [Beholder(200,"Shmiddy"),Beholder(200,"Steven"),Beholder(200,"Joe")]

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((SCREEN_W,SCREEN_H))
        self.surface = pygame.display.get_surface()
        self.renderer = CardRenderer()
        self.deck = None
        self.ui = TitleScreen()
        self.nextUI = None

    def nextScene(self):
        def next():
            self.state = GameState(list(map(getCard,self.deck)))
            self.state.enemies = testEnemies
            self.nextUI = BattleIdle()
        self.nextUI = CardReward(instantiateDeck([CARD_DIVINATION,CARD_FIREBLAST,CARD_MANARUNE]),next)

    def run(self):
        lastTime = pygame.time.get_ticks()
        while True:
            oldUI = self.ui
            self.draw()
            self.inputs()
            self.update(pygame.time.get_ticks() - lastTime)
            lastTime = pygame.time.get_ticks()
            if self.nextUI != None:
                self.ui = self.nextUI
                self.nextUI = None
            if self.ui != oldUI:
                oldUI.exit(self)


    def draw(self):
        self.surface.fill((100,100,100))
        self.ui.draw(self)
        pygame.display.flip()

    def inputs(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if not isinstance(self.ui,Paused):
                        self.ui = Paused(self.ui,self.surface.copy())
                    else:
                        self.ui.unpause(self)
            else:
                self.ui.input(self,event)


    def update(self,dt):
        self.ui.update(self,dt/1000)
