from cards import *

class Deck:
    def __init__(self,name,list,image,blurb):
        self.name = name
        self.list = list
        self.image = image
        self.blurb = blurb
    def tooltip_text(self):
        text = "Cards: \n"
        already = []
        for card in self.list:
            if card not in already:
                text += f"{self.list.count(card)} {cardPrototypes[card].name}\n"
                already.append(card)
        return text

decks = []

decks.append(Deck("The Pyromancer",[CARD_FIREBLAST]*5 + [CARD_MANARUNE]*3 + [CARD_DIVINATION]*2,"assets/sword.png","Roast your enemies!"))
decks.append(Deck("The Diviner",[CARD_FIREBLAST]*2 + [CARD_MANARUNE]*5 + [CARD_DIVINATION]*3,"assets/manabottle.png","Learn of arcane knowledge."))
