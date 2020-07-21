import copy
import loader
from state import Zone,Interrupt

N_CARDS = 10

CARD_FIREBLAST,CARD_CANTRIP,CARD_RITUAL,CARD_DIVINATION,CARD_MANARUNE,CARD_DRAWRUNE,CARD_NAME,CARD_CRUNCH,CARD_COPY,CARD_TUTOR = range(N_CARDS)

N_TARGET_MODES = 5

NO_TARGETS, TARGET_ENEMY, TARGET_RUNE, TARGET_CARD, TARGET_CARD_IN_ZONE = range(N_TARGET_MODES)

class Card:
    def __init__(self,cost,name,image,text,color,targeting,tooltips=[],target_zone=None):
        self.cost = cost
        self.name = name
        self.image = image
        self.text = text
        self.color = color
        self.highlight = False
        self.tooltips = tooltips
        self.showTooltips = True
        self.targeting = targeting
        if self.targeting == TARGET_CARD_IN_ZONE:
            self.target_zone = target_zone
            assert target_zone != None
        self.is_rune = False
    def play(self,state):
        pass

class Rune(Card):
    def __init__(self,*args,rune_tooltips=[],**kwargs):
        Card.__init__(self,*args,**kwargs)
        self.is_rune = True
        self.rune_tooltips = rune_tooltips + [f"(Card Text:)\n{args[3]}"]
    def rune_eot(self,state):
        pass
    def rune_image(self):
        pass

NORMAL_COLOR = (70,70,70)
RUNE_COLOR = (70,70,150)

cardPrototypes = [None for i in range(N_CARDS)]

class Fireblast(Card):
    def play(self,state,enemy):
        state.deal_damage(enemy,7)

cardPrototypes[CARD_FIREBLAST] = Fireblast(1,"Fireblast","assets/dummy.png","Deal 7 Damage.",NORMAL_COLOR,TARGET_ENEMY)

class Cantrip(Card):
    def play(self,state):
        state.draw(1)

cardPrototypes[CARD_CANTRIP] = Cantrip(1,"Cantrip","assets/dummy.png","Draw 1 card.",NORMAL_COLOR,NO_TARGETS)

class Ritual(Card):
    def play(self,state):
        state.mana += 3

cardPrototypes[CARD_RITUAL] = Ritual(1,"Ritual","assets/dummy.png","Add 3 |Mana|.",NORMAL_COLOR,NO_TARGETS)

class Divination(Card):
    def play(self,state):
        state.draw(2)

cardPrototypes[CARD_DIVINATION] = Divination(3,"Divination","assets/dummy.png","Draw 2 cards.",NORMAL_COLOR,NO_TARGETS)

class ManaRune(Rune):
    def rune_eot(self,state):
        state.mana += 1
    def rune_image(self):
        return loader.loader.get_image_size("assets/manabottle.png",(100,100))

cardPrototypes[CARD_MANARUNE] = ManaRune(0,"Mana Rune","assets/dummy.png","/End of Turn/:\n Add 1 |Mana|.",RUNE_COLOR,NO_TARGETS,tooltips=["LOL"])

class DrawRune(Rune):
    def rune_eot(self,state):
        state.draw(1)
    def rune_image(self):
        return loader.loader.get_image_size("assets/manabottle.png",(100,100))

cardPrototypes[CARD_DRAWRUNE] = DrawRune(2,"Mind Rune","assets/dummy.png","/End of Turn/:\n Draw 1 card.",RUNE_COLOR,NO_TARGETS)

class Name(Card):
    def play(self,state,target):
        print(target.name)

cardPrototypes[CARD_NAME] = Name(1,"Name","assets/dummy.png","Check an enemy's name.",NORMAL_COLOR,TARGET_ENEMY)

class Crunch(Card):
    def play(self,state,target):
        location = state.locateCard(target)
        assert location[0] == Zone.RUNES
        card = state.runes.pop(location[1])
        state.discard.append(card)

cardPrototypes[CARD_CRUNCH] = Crunch(1,"Crunch","assets/dummy.png","Discard a rune.",NORMAL_COLOR,TARGET_RUNE)

class Copy(Card):
    def play(self,state,target):
        state.hand.append(copy.deepcopy(target))

cardPrototypes[CARD_COPY] = Copy(1,"Copy","assets/dummy.png","Copy a card from\n your hand.",NORMAL_COLOR,TARGET_CARD)

class Tutor(Card):
    def play(self,state,target):
        location = state.locateCard(target)
        assert location[0] == Zone.DECK
        card = state.deck.pop(location[1])
        state.hand.append(card)

cardPrototypes[CARD_TUTOR] = Tutor(1,"Tutor","assets/dummy.png","Search your deck \n for a card and put \n it in your hand.",NORMAL_COLOR,TARGET_CARD_IN_ZONE,target_zone=Zone.DECK)

def getCard(id):
    return copy.deepcopy(cardPrototypes[id])

instantiateDeck = lambda x: list(map(getCard,x))
