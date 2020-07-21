from loader import loader
import pygame
import random
from render import HEALTH_X,HEALTH_Y
from animation import *


class Intention:
    def icon(self):
        return None
    def number(self):
        return None
    def effect(self,state):
        pass
    def animation(self,ui):
        return Animation()
    def falter(self,amount):
        pass

class Attack(Intention):
    def __init__(self,amount):
        self.amount = amount
    def icon(self):
        return "assets/sword.png"
    def number(self):
        return self.amount
    def effect(self,state):
        state.health -= self.amount
    def falter(self,amount):
        self.amount -= amount
        self.amount = max(0,self.amount)
    def animations(self,owner,state,ui):
        index = state.enemies.index(owner)
        rect = ui.enemyHitboxes[index]
        center = Vector(*pygame.rect.Rect(rect).center)
        return [MoveIconToPos(owner,center,Vector(HEALTH_X,HEALTH_Y),self.icon())]

class Sap(Intention):
    def icon(self):
        return "assets/bolt.png"
    def effect(self,state):
        for i in state.hand:
            i.cost += 1
    def animations(self,owner,state,ui):
        index = state.enemies.index(owner)
        rect = ui.enemyHitboxes[index]
        center = Vector(*pygame.rect.Rect(rect).center)
        results = []
        for hitbox in ui.cardHitboxes:
            c2 = Vector(*pygame.rect.Rect(hitbox).topleft)
            results.append(MoveIconToPos(owner,center,c2,self.icon()))
        return results



class Enemy:
    def get_tooltips(self):
        return ["Test tooltip"]
    def width(self):
        return self.image.get_rect().w
    def height(self):
        return self.image.get_rect().h
    def health(self):
        return 0
    def damage(self,n):
        pass

class Beholder(Enemy):
    def __init__(self,size,name):
        self.image = loader.get_image_size("assets/beholder.png",(size,size))
        self.size = size
        self.name = name
        self.hp = 10
        self.intent = Attack(int(random.random()*20))
    def damage(self,amount):
        self.hp -= amount
        self.intent.falter(amount)
    def health(self):
        return self.hp
    def take_turn(self,state):
        self.intent.effect(state)
        self.intent = Sap()
