import pygame
from loader import loader
from vector import Vector
from state import Zone
from render import CARD_W,CARD_H,ICON_SIZE

class Animation:
    def __init__(self):
        self.elapsed = True
    def update(self,game,dt):
        pass
    def draw(self,owner,game):
        pass
    def setKwargs(self,game):
        self.kwargs = {}

CARD_SPEED = 900

def getPosition(state,zone,hand,runes,icons,play):
    (z,location) = zone
    if z == Zone.HAND:
        return Vector(*hand[location][:2])
    elif z in [Zone.DECK,Zone.STOCK,Zone.DISCARD]:
        return Vector(*icons[z][:2])
    elif z == Zone.RUNES:
        return Vector(*runes[location][:2])
    elif z == Zone.PLAY:
        return play


def getCardMovementAnimation(state,fromZone,toZone,oldHand,newHand,oldRunes,newRunes,icons,play):
    p1 = getPosition(state,fromZone,oldHand,oldRunes,icons,play)
    p2 = getPosition(state,toZone,newHand,newRunes,icons,play)
    target = state.get_zone(toZone[0])[toZone[1]]
    if fromZone[0] == Zone.RUNES:
        return MoveRuneTo(target,p1,p2)
    if fromZone[0] == Zone.NONE:
        return GrowCard(target,p2)
    return MoveCardTo(target,p1,p2)

def getEnemyMovementAnimation(oldState,state,fromZone,toZone,olds,news):
    if fromZone == None:
        assert False
        return None

    p1 = Vector(*olds[fromZone][:2])

    if toZone == None:
        return ShrinkEnemy(oldState.enemies[fromZone],p1)

    p2 = Vector(*news[toZone][:2])
    return MoveEnemy(state.enemies[toZone],p1,p2)

class MoveObject(Animation):
    def __init__(self,target,startPos,destination):
        self.target = target
        self.destination = destination
        self.delta = destination - startPos
        self.pos = startPos
        self.elapsed = False
        self.t = self.delta.magnitude()/CARD_SPEED
        self.kwargs = {}
    def setKwargs(self,state):
        if self.target in state.hand:
            self.kwargs = {"skips":[state.hand.index(self.target)]}
        if self.target in state.runes:
            self.kwargs = {"skipRunes":[state.runes.index(self.target)]}
    def update(self,game,dt):
        if self.t <= 0:
            self.elapsed = True
            return
        self.t -= dt
        self.pos += self.delta.normalize() * CARD_SPEED * dt

class MoveRuneTo(MoveObject):
    def draw(self,owner,game):
        if self.elapsed:
            game.surface.blit(self.target.rune_image(),self.destination)
            return
        game.surface.blit(self.target.rune_image(),self.pos)


class MoveCardTo(MoveObject):
    def draw(self,owner,game):
        if self.elapsed:
            game.renderer.draw(game.surface,self.destination,self.target)
            return
        game.renderer.draw(game.surface,self.pos,self.target)

class GrowCard(Animation):
    def __init__(self,target,position,time=1):
        self.target = target
        self.cardsurf = None
        self.t = 0
        self.maxt = time
        self.elapsed = False
        self.position = position
    def setKwargs(self,state):
        if self.target in state.hand:
            self.kwargs = {"skips":[state.hand.index(self.target)]}
    def draw(self,owner,game):
        if self.elapsed:
            game.surface.blit(self.cardsurf,self.position)
        else:
            if self.cardsurf == None:
                self.cardsurf = pygame.Surface((CARD_W,CARD_H),flags=pygame.SRCALPHA)
                self.cardsurf.fill((0,0,0,0))
                game.renderer.draw(self.cardsurf,Vector(0,0),self.target)
            cardsize = Vector(CARD_W,CARD_H)
            size = (cardsize * (self.t/self.maxt)).toInt()
            s2 = pygame.transform.scale(self.cardsurf,size)
            game.surface.blit(s2,self.position + cardsize/2 - size/2)
    def update(self,game,dt):
        if self.t >= self.maxt:
            self.elapsed = True
            return
        self.t += dt

class MoveEnemy(MoveObject):
    def setKwargs(self,state):
        if self.target in state.enemies:
            self.kwargs = {"skipEnemies":[state.enemies.index(self.target)]}
    def draw(self,owner,game):
        game.surface.blit(self.target.image,self.pos.toInt())

class ShrinkEnemy(Animation):
    def __init__(self,target,position,time=1):
        self.target = target
        self.t = 0
        self.maxt = time
        self.elapsed = False
        self.position = position
    def draw(self,owner,game):
        if not self.elapsed:
            enemysize = Vector(self.target.width(),self.target.height())
            size = (enemysize * max(0,1 - self.t/self.maxt)).toInt()
            s2 = pygame.transform.scale(self.target.image,size)
            game.surface.blit(s2,self.position + enemysize/2 - size/2)
    def update(self,game,dt):
        if self.t >= self.maxt:
            self.elapsed = True
            return
        self.t += dt

class MoveIconToPos(Animation):
    def __init__(self,owner,start,end,icon):
        self.owner = owner
        self.end = end
        self.delta = end - start
        self.pos = start
        self.elapsed = False
        self.t = self.delta.magnitude()/CARD_SPEED
        self.kwargs = {}
        self.image = loader.get_image_size(icon,(ICON_SIZE,ICON_SIZE))
    def setKwargs(self,state):
        self.kwargs = {"skipEnemyIcons":[state.enemies.index(self.owner)]}
    def update(self,game,dt):
        if self.t <= 0:
            self.elapsed = True
            return
        self.t -= dt
        self.pos += self.delta.normalize() * CARD_SPEED * dt
    def draw(self,owner,game):
        if self.elapsed:
            game.surface.blit(self.image,self.end)
            return
        game.surface.blit(self.image,self.pos)
