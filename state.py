import random

class Zone:
    HAND,DISCARD,DECK,STOCK,PLAY,RUNES,NONE = range(7)

class Interrupt:
    (CHOOSE_CARD) = range(1)
    def __init__(self,mode,callback,zone=None):
        self.mode = mode
        self.callback = callback
        if callback == Interrupt.CHOOSE_CARD:
            assert zone!=None
            self.zone = zone

class GameState:
    def __init__(self,deck):
        self.deck = []
        self.hand = []
        self.discard = deck
        self.stock = []
        self.enemies = []
        self.runes = []
        self.inPlay = None
        self.mana = 0
        self.interrupt = None
        self.health = 50
        self.draw(5)

    def find_enemy(self,enemy):
        if enemy not in self.enemies:
            return None
        return self.enemies.index(enemy)

    def deal_damage(self,enemy,amount):
        enemy.damage(amount)
        if enemy.health() < 0:
            index = self.find_enemy(enemy)
            self.enemies.pop(index)


    def shallow_copy(self):
        g_ = GameState([])
        g_.discard = list(self.discard)
        g_.deck = list(self.deck)
        g_.hand = list(self.hand)
        g_.stock = list(self.stock)
        g_.runes = list(self.runes)
        g_.inPlay = self.inPlay
        g_.mana = self.mana
        g_.enemies = list(self.enemies)
        return g_

    def get_zone(self,zone):
        if zone == Zone.HAND:
            return self.hand
        elif zone == Zone.DISCARD:
            return self.discard
        elif zone == Zone.DECK:
            return self.deck
        elif zone == Zone.STOCK:
            return self.stock
        elif zone == Zone.RUNES:
            return self.runes
        elif zone == Zone.PLAY:
            return [self.inPlay] if self.inPlay else []

    def draw(self,n=1):
        for i in range(n):
            if len(self.hand) == 10:
                return
            if len(self.deck) == 0:
                if len(self.discard) != 0:
                    self.deck = self.discard
                    self.discard = []
                    random.shuffle(self.deck)
                else:
                    return
            self.hand.insert(0,self.deck.pop(0))

    def locateCard(self,card):
        if card in self.hand:
            return (Zone.HAND,self.hand.index(card))
        elif card in self.discard:
            return (Zone.DISCARD,self.discard.index(card))
        elif card in self.deck:
            return (Zone.DECK,self.deck.index(card))
        elif card in self.stock:
            return (Zone.STOCK,self.deck.index(card))
        elif card in self.runes:
            return (Zone.RUNES,self.runes.index(card))
        elif card == self.inPlay:
            return (Zone.PLAY,0)
        else:
            return (Zone.NONE,-1)

    def swapCards(self,a,b):
        self.hand[a],self.hand[b] = self.hand[b],self.hand[a]

    def moveToPlay(self,index):
        self.inPlay = self.hand.pop(index)

    def returnFromPlay(self,index):
        self.hand.insert(index,self.inPlay)
        self.inPlay = None

    def canPlay(self,card):
        if card.is_rune and len(self.runes) == 13:
            return False
        return card.cost <= self.mana

    def playCard(self,*args):
        self.mana -= self.inPlay.cost
        assert self.mana >= 0
        self.inPlay.play(self,*args)
        if self.inPlay.is_rune:
            self.runes.append(self.inPlay)
        else:
            self.discard.append(self.inPlay)
        self.inPlay = None

    def end_turn(self):
        self.draw(1)
        self.mana = 0
        for rune in self.runes:
            rune.rune_eot(self)

    def enemyTurn(self):
        for i in self.enemies:
            i.take_turn(self)
