import pygame
import copy
from pygame.locals import *
from vector import Vector
from util import mergeDicts
from animation import MoveCardTo,getCardMovementAnimation,getEnemyMovementAnimation
from cards import *
from arrow import Arrow
from decks import decks
from state import Zone

#The UI is implemented as a Finite State Machine.

def drawBattleScreen(self,game,kwargs={}):
    game.renderer.drawMana(game.surface,game.state)
    self.viewHitboxes = game.renderer.drawDecks(game.surface,game.state)
    self.cardHitboxes = game.renderer.drawHand(game.surface,game.state.hand,**kwargs)
    self.enemyHitboxes = game.renderer.drawEnemies(game.surface,game.state.enemies,**kwargs)
    self.runeHitboxes = game.renderer.drawRunes(game.surface,game.state.runes,**kwargs)
    self.endTurnHitbox = game.renderer.drawEndButton(game.surface)
    game.renderer.drawPlayerHealth(game.surface,game.state.health)

class BaseUI:
    def draw(self,game):
        pass
    def input(self,game,event):
        pass
    def update(self,game,dt):
        pass
    def exit(self,game):
        pass

class TitleScreen(BaseUI):
    def __init__(self):
        self.hover = []
        self.buttonRects = []
    def draw(self,game):
        self.buttonRects = game.renderer.drawTitleScreen(game.surface,self.hover)
    def clicked(self,i,game):
        if i == 0:
            game.nextUI = StartGame()
        if i == 1:
            game.nextUI = CreditsScreen()
        if i == 2:
            quit()
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.buttonRects)):
                if pygame.rect.Rect(self.buttonRects[i]).collidepoint(*event.pos):
                        self.clicked(i,game)

        mousepos = pygame.mouse.get_pos()
        for i in range(len(self.buttonRects)):
            if pygame.rect.Rect(self.buttonRects[i]).collidepoint(mousepos):
                self.hover = [i]
                break
        else:
            self.hover = []

class CreditsScreen(BaseUI):
    def __init__(self):
        self.hover = []
        self.clicked = []
    def draw(self,game):
        self.backRect = game.renderer.drawCreditsScreen(game.surface)
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if pygame.rect.Rect(self.backRect).collidepoint(*event.pos):
                game.nextUI = TitleScreen()

class StartGame(BaseUI):
    def __init__(self):
        self.hover = []
        self.clicked = []
    def draw(self,game):
        (self.choose_hitboxes,self.beginRect,self.backRect) = game.renderer.drawDeckChooser(game.surface,decks,self.hover,self.clicked)
        if len(self.hover):
            pos = pygame.mouse.get_pos()
            game.renderer.drawTooltips(game.surface,pos[0],pos[1],[decks[self.hover[0]].tooltip_text()])
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.choose_hitboxes)):
                if pygame.rect.Rect(self.choose_hitboxes[i]).collidepoint(*event.pos):
                        self.clicked = [i]
            if pygame.rect.Rect(self.beginRect).collidepoint(*event.pos) and len(self.clicked):
                game.deck = decks[self.clicked[0]].list
                game.nextScene()
            if pygame.rect.Rect(self.backRect).collidepoint(*event.pos):
                game.nextUI = TitleScreen()

        mousepos = pygame.mouse.get_pos()
        for i in range(len(self.choose_hitboxes)):
            if pygame.rect.Rect(self.choose_hitboxes[i]).collidepoint(mousepos):
                self.hover = [i]
                break
        else:
            self.hover = []

class Paused(BaseUI):
    def __init__(self,previous,background):
        self.background = background
        self.previous = previous
        alphamask = pygame.Surface(self.background.get_rect().size,pygame.SRCALPHA)
        alphamask.fill((255,255,255,160))
        self.background.blit(alphamask,(0,0))
        self.hover = []
        self.buttonRects = []
    def unpause(self,game):
        game.nextUI = self.previous
    def draw(self,game):
        game.surface.blit(self.background,(0,0))
        self.buttonRects = game.renderer.drawPauseMenu(game.surface,self.hover)
    def clicked(self,i,game):
        if i == 0:
            self.unpause(game)
        if i == 1:
            game.nextUI = StartGame()
        if i == 2:
            quit()
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.buttonRects)):
                if pygame.rect.Rect(self.buttonRects[i]).collidepoint(*event.pos):
                        self.clicked(i,game)

        mousepos = pygame.mouse.get_pos()
        for i in range(len(self.buttonRects)):
            if pygame.rect.Rect(self.buttonRects[i]).collidepoint(mousepos):
                self.hover = [i]
                break
        else:
            self.hover = []

class CardReward(BaseUI):
    def __init__(self,cards,next):
        self.cards = cards
        self.next = next
        self.hover = []
        self.selected = []
        self.deckHitbox = None
    def draw(self,game):
        (self.cardRects,self.buttonRect,self.deckHitbox) = game.renderer.drawCardReward(game.surface,self.cards,len(game.deck),hover=self.hover,highlights=self.selected)
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.cardRects)):
                if pygame.rect.Rect(self.cardRects[i]).collidepoint(*event.pos):
                    if i not in self.selected:
                        self.selected = [i]
                    else:
                        self.selected = []
                if pygame.rect.Rect(self.buttonRect).collidepoint(*event.pos):
                    game.deck += [self.cards[c].id for c in self.selected]
                    self.next()
                if pygame.rect.Rect(self.deckHitbox).collidepoint(*event.pos):
                    game.nextUI = BattleViewingCards(game.surface.copy(),Zone.DECK,zone=instantiateDeck(game.deck),next=self)

        mousepos = pygame.mouse.get_pos()
        for i in range(len(self.cardRects)):
            if pygame.rect.Rect(self.cardRects[i]).collidepoint(mousepos):
                self.hover = [i]
                break
        else:
            self.hover = []

class PlayUI(BaseUI):
    def animateGameChange(self,game,change,endTurn=False):
        old = game.state.shallow_copy()
        change(game.state)
        movements = []
        checked = []

        # Diff cards

        cards = game.state.hand + old.hand + game.state.runes + old.runes +  [old.inPlay]
        cards = list(filter(lambda x: x!= None,cards))
        for card in cards:
            if card not in checked:
                movements.append((old.locateCard(card),game.state.locateCard(card)))
                checked.append(card)
        oldRects = self.cardHitboxes
        newRects = game.renderer.drawHand(game.surface,game.state.hand,draw=False)
        oldRunes = self.runeHitboxes
        newRunes = game.renderer.drawRunes(game.surface,game.state.runes,draw=False)
        iconRects = self.viewHitboxes
        try:
            pos = self.cardPos
        except:
            pos = None
        animations = map(lambda x: getCardMovementAnimation(game.state,*x,oldRects,newRects,oldRunes,newRunes,iconRects,pos),movements)
        animations = list(filter(lambda x: x!=None,animations))

        enemies = game.state.enemies + old.enemies
        checked = []
        movements=[]
        for enemy in enemies:
            if enemy not in checked:
                movements.append((old.find_enemy(enemy),game.state.find_enemy(enemy)))
                checked.append(enemy)
        oldEnemies = self.enemyHitboxes
        newEnemies = game.renderer.drawEnemies(game.surface,game.state.enemies,draw=False)
        eAnims = map(lambda x: getEnemyMovementAnimation(old,game.state,*x,oldEnemies,newEnemies),movements)
        if any(map(lambda x: x[0] != x[1],movements)):
            animations += list(filter(lambda x:x!=None,eAnims))

        def next():
            game.nextUI = BattleIdle()
            if endTurn:
                def next2():
                    game.nextUI = BattleIdle()
                    game.state.enemyTurn()
                nextAnims = sum(map(lambda e: e.intent.animations(e,game.state,game.ui),game.state.enemies),[])
                for i in nextAnims:
                    i.setKwargs(game.state)
                game.nextUI = BattleAnimating(nextAnims,next2)

        for i in animations:
            i.setKwargs(game.state)
        game.nextUI = BattleAnimating(animations,next)

    def tryPlayCard(self,game,*args,fail=False):
        game.state.moveToPlay(self.cardN)
        if fail or not game.state.canPlay(game.state.inPlay):
            # insert a dummy to mimic an empty spot
            game.state.hand.insert(self.cardN,None)
        def change(state):
            if state.canPlay(state.inPlay) and not fail:
                state.playCard(*args)
            else:
                state.hand[self.cardN] = state.inPlay
                state.inPlay = None
        self.animateGameChange(game,change)

class BattleIdle(PlayUI):
    def __init__(self):
        self.hover = []
        self.runehover = []
        self.enemyhover = []
    def draw(self,game):
        for i in game.state.hand:
            i.highlight = game.state.canPlay(i)
        drawBattleScreen(self,game,kwargs={"highlights":list(filter(game.state.canPlay,game.state.hand)),"hover":self.hover,"runehover":self.runehover,"enemyhover":self.enemyhover})
    def input(self,game,event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.cardHitboxes)):
                if pygame.rect.Rect(self.cardHitboxes[i]).collidepoint(*event.pos):
                    choice = [BattleHoldingCard,BattleTargetingEnemy,BattleTargetingRune,BattleTargetingCard,BattleZTargeting][game.state.hand[i].targeting]
                    game.nextUI = choice(i,Vector(*self.cardHitboxes[i][:2]))
                    return
            for zone in self.viewHitboxes:
                if pygame.rect.Rect(self.viewHitboxes[zone]).collidepoint(*event.pos):
                    game.nextUI = BattleViewingCards(game.surface.copy(),zone)
            if pygame.rect.Rect(self.endTurnHitbox).collidepoint(*event.pos):
                def change(state):
                    state.end_turn()
                self.animateGameChange(game,change,lambda st:st.end_turn())

        mousepos = pygame.mouse.get_pos()
        for i in range(len(self.cardHitboxes)):
            if pygame.rect.Rect(self.cardHitboxes[i]).collidepoint(mousepos):
                self.hover = [game.state.hand[i]]
                break
        else:
            self.hover = []

        for i in range(len(self.runeHitboxes)):
            if pygame.rect.Rect(self.runeHitboxes[i]).collidepoint(mousepos):
                self.runehover = [i]
                break
        else:
            self.runehover = []

        for i in range(len(self.enemyHitboxes)):
            if pygame.rect.Rect(self.enemyHitboxes[i]).collidepoint(mousepos):
                self.enemyhover = [i]
                break
        else:
            self.enemyhover = []


class BattleHoldingCard(PlayUI):
    def __init__(self,cardN,cardPos):
        self.cardN = cardN
        self.cardPos = cardPos

    def draw(self,game):
        drawBattleScreen(self,game,kwargs={"skips":[self.cardN]})
        game.renderer.draw(game.surface,self.cardPos,game.state.hand[self.cardN])

    def input(self,game,event):
        if event.type == MOUSEMOTION:
            self.cardPos += Vector(*event.rel)
        if event.type == MOUSEBUTTONUP and event.button == 1:
            for i in range(len(self.cardHitboxes)):
                if pygame.rect.Rect((self.cardHitboxes[i])).collidepoint(*event.pos):
                    def change(state):
                        state.swapCards(self.cardN,i)
                    self.animateGameChange(game,change)
                    break
            else:
                self.doPlay(game)

    def doPlay(self,game):
        self.tryPlayCard(game)

class BattleTargeting(PlayUI):
    def __init__(self,cardN,cardPos):
        self.arrow = Arrow(Vector(*pygame.mouse.get_pos()))
        self.cardN = cardN
        self.cardPos = cardPos
        self.arrow.set_destination(cardPos)

    def draw(self,game):
        drawBattleScreen(self,game,kwargs={"skips":[self.cardN]})
        game.renderer.draw(game.surface,self.cardPos,game.state.hand[self.cardN])
        self.arrow.draw(game.surface)

    def input(self,game,event):
        self.arrow.set_destination(Vector(*pygame.mouse.get_pos()))

        hitboxes = self.findHitboxes()
        targets = self.findTargets(game)

        if event.type == MOUSEBUTTONUP and event.button == 1:
            for i in range(len(hitboxes)):
                if pygame.rect.Rect((hitboxes[i])).collidepoint(*event.pos):
                    self.tryPlayCard(game,targets[i])
                    break
            else:
                game.nextUI = BattleIdle()

class BattleTargetingEnemy(BattleTargeting):
    def findHitboxes(self):
        return self.enemyHitboxes
    def findTargets(self,game):
        return game.state.enemies

class BattleTargetingRune(BattleTargeting):
    def findHitboxes(self):
        return self.runeHitboxes
    def findTargets(self,game):
        return game.state.runes

class BattleTargetingCard(BattleTargeting):
    def findHitboxes(self):
        return self.cardHitboxes
    def findTargets(self,game):
        return game.state.hand

class BattleZTargeting(BattleHoldingCard):
    def doPlay(self,game):
        if not game.state.canPlay(game.state.hand[self.cardN]):
            self.tryPlayCard(game)
        else:
            game.nextUI = BattleChoosingCard(game.surface.copy(),game.state.hand[self.cardN].target_zone,self)

class BattleChoosingCard(PlayUI):
    def __init__(self,background,which,parent):
        self.background = background
        self.which = which
        alphamask = pygame.Surface(self.background.get_rect().size,pygame.SRCALPHA)
        alphamask.fill((255,255,255,160))
        self.background.blit(alphamask,(0,0))
        self.scroll = 0
        self.hover = []
        self.__dict__.update(parent.__dict__)
    def draw(self,game):
        game.surface.blit(self.background,(0,0))
        self.exitRect = game.renderer.drawExitViewer(game.surface)
        self.cards = game.renderer.drawCardPile(game.surface,game.state.get_zone(self.which),self.which,self.scroll,self.hover,choose=True)
    def input(self,game,event):
        for (rect,card) in self.cards:
            if pygame.rect.Rect(rect).collidepoint(*pygame.mouse.get_pos()):
                self.hover = [card]
                break
        else:
            self.hover = []
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if pygame.rect.Rect(self.exitRect).collidepoint(*event.pos):
                self.tryPlayCard(game,fail=True)
            for (rect,card) in self.cards:
                if pygame.rect.Rect(rect).collidepoint(*event.pos):
                    self.tryPlayCard(game,card)
                    break
        elif event.type == MOUSEBUTTONDOWN and event.button == 4:
            self.scroll -= 1
        elif event.type == MOUSEBUTTONDOWN and event.button == 5:
            self.scroll +=1


class BattleViewingCards(BaseUI):
    def __init__(self,background,which,zone=None,next=BattleIdle()):
        self.background = background
        self.which = which
        self.zone = zone
        alphamask = pygame.Surface(self.background.get_rect().size,pygame.SRCALPHA)
        alphamask.fill((255,255,255,160))
        self.background.blit(alphamask,(0,0))
        self.scroll = 0
        self.hover = []
        self.next = next
    def draw(self,game):
        game.surface.blit(self.background,(0,0))
        self.exitRect = game.renderer.drawExitViewer(game.surface)
        self.cards = game.renderer.drawCardPile(game.surface,self.zone or game.state.get_zone(self.which),self.which,self.scroll,self.hover)
    def input(self,game,event):
        for (rect,card) in self.cards:
            if pygame.rect.Rect(rect).collidepoint(*pygame.mouse.get_pos()):
                self.hover = [card]
                break
        else:
            self.hover = []
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if pygame.rect.Rect(self.exitRect).collidepoint(*event.pos):
                game.nextUI = self.next
        elif event.type == MOUSEBUTTONDOWN and event.button == 4:
            self.scroll -= 1
        elif event.type == MOUSEBUTTONDOWN and event.button == 5:
            self.scroll +=1

class BattleAnimating(BaseUI):
    def __init__(self,animations,next):
        self.animations = animations
        self.next = next
        self.kwargs = mergeDicts([i.kwargs for i in animations])
    def draw(self,game):
        drawBattleScreen(self,game,kwargs=self.kwargs)
        for i in self.animations:
            i.draw(self,game)
    def update(self,game,dt):
        for i in self.animations:
            i.update(game,dt)
        if all(map(lambda x:x.elapsed,self.animations)):
            self.next()
