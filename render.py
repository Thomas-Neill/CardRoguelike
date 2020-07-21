import pygame
from loader import loader
from vector import Vector
import math
from state import Zone

SCREEN_W = 1800
SCREEN_H = 900

CARD_W = 160
CARD_H = 230

TOOLTIP_W = 150
TOOLTIP_H = 100

HIGHLIGHT_SIZE = 3
BORDER_COLOR = (0,0,0)
HIGHLIGHT_COLOR = (57,255,20)

TOOLTIP_COLOR = (170,170,170)

MASSIVE_TITLE_SIZE = 60
BIG_TITLE_SIZE = 30
TITLE_SIZE = 18
TEXT_SIZE = 14

MARGIN_SIZE = 10

IMAGE_W = CARD_W-2*MARGIN_SIZE
IMAGE_H = int(IMAGE_W*.7)

HAND_H = SCREEN_H - CARD_H - MARGIN_SIZE

MANA_COLOR = (255,215,0)
MANA_RADIUS = 10

ICON_SIZE = 40

MANA_X = MARGIN_SIZE + MANA_RADIUS*2
MANA_Y = HAND_H - MARGIN_SIZE - MANA_RADIUS*2

DECK_X = MARGIN_SIZE + MANA_RADIUS*4 + MARGIN_SIZE
DECK_Y = HAND_H - MARGIN_SIZE - ICON_SIZE

DISCARD_X = SCREEN_W - ICON_SIZE - MARGIN_SIZE - 30
DISCARD_Y = DECK_Y

HEALTH_Y = DECK_Y - MARGIN_SIZE*2 - ICON_SIZE
HEALTH_X = MANA_X

STOCK_X = DISCARD_X
STOCK_Y = DISCARD_Y - MARGIN_SIZE - ICON_SIZE

ROW_SIZE = 5
ROW_WIDTH = CARD_W*ROW_SIZE + (ROW_SIZE-1)*MARGIN_SIZE*2

SCROLLBAR_W = 10
SCROLLBAR_COLOR = (100,100,100)
SCROLLBAR_BUTTON_COLOR = (0,0,0)

END_BUTTON_W = 100
END_BUTTON_H = TITLE_SIZE + MARGIN_SIZE*2
END_BUTTON_COLOR = (70,70,70)
END_BUTTON_Y = STOCK_Y - MARGIN_SIZE

BACKBUTTON_X = MARGIN_SIZE*5
STARTBUTTON_X = SCREEN_W - MARGIN_SIZE*20
STARTBUTTON_Y = SCREEN_H - MARGIN_SIZE*10
STARTBUTTON_W = MARGIN_SIZE*15
STARTBUTTON_H = MARGIN_SIZE*7

TITLE_STRINGS = {Zone.DECK:"Deck",Zone.STOCK:"Stock Pile",Zone.DISCARD:"Discard Pile"}
SUB_STRINGS = {Zone.DECK:"You draw one card from your deck at the start of each turn.\n /(Displayed in random order).",
               Zone.STOCK:"At the start of your turn, return one |Stocked| card of your choice from here to your hand.",
               Zone.DISCARD:"If your deck runs out of cards, these will be reshuffled and returned to your deck."}

TEXTBOX_COLOR = (170,170,170)

def writeText(fonts,surface,text,rect):
    lines = text.split('\n')
    target_h = rect.y + MARGIN_SIZE//4
    for line in lines:
        renders = []
        bold = False
        for boldSegment in line.strip().split("|"):
            italic = False
            for chunk in boldSegment.split("/"):
                if italic:
                    rendered = fonts[2].render(chunk,True,(0,0,0))
                elif bold:
                    rendered = fonts[1].render(chunk,True,(0,0,0))
                else:
                    rendered = fonts[0].render(chunk,True,(0,0,0))
                italic = not italic
                renders.append(rendered)
            bold = not bold

        x = rect.centerx - sum(map(lambda x:x.get_rect().w//2,renders))
        for rendered in renders:
            surface.blit(rendered,(x,target_h))
            x += rendered.get_rect().w
        target_h += MARGIN_SIZE//4 + rendered.get_rect().h



class CardRenderer:
    def __init__(self):
        self.massiveTitleFont = pygame.font.Font("fonts/Caladea-Regular.ttf",MASSIVE_TITLE_SIZE)
        self.bigTitleFont = pygame.font.Font("fonts/Caladea-Regular.ttf",BIG_TITLE_SIZE)
        self.titleFont = pygame.font.Font("fonts/Caladea-Regular.ttf",TITLE_SIZE)
        self.boldTitleFont = pygame.font.Font("fonts/Caladea-Bold.ttf",TITLE_SIZE)
        self.italicTitleFont = pygame.font.Font("fonts/Caladea-Italic.ttf",TITLE_SIZE)
        self.textFont = pygame.font.Font("fonts/Caladea-Regular.ttf",TEXT_SIZE)
        self.boldFont = pygame.font.Font("fonts/Caladea-Bold.ttf",TEXT_SIZE)
        self.italicFont = pygame.font.Font("fonts/Caladea-Italic.ttf",TEXT_SIZE)

    def draw(self,surface,position,cardData):
        #Render card frame & image
        cardRect = (*position,CARD_W,CARD_H)
        pygame.draw.rect(surface,HIGHLIGHT_COLOR if cardData.highlight else BORDER_COLOR,cardRect,border_radius=11)
        innerCardRect = (*(position + Vector(HIGHLIGHT_SIZE,HIGHLIGHT_SIZE)),CARD_W-HIGHLIGHT_SIZE*2,CARD_H-HIGHLIGHT_SIZE*2)
        pygame.draw.rect(surface,cardData.color,innerCardRect,border_radius=11)
        image = loader.get_image_size(cardData.image,(IMAGE_W,IMAGE_H))
        surface.blit(image,position + Vector(MARGIN_SIZE,TITLE_SIZE+MARGIN_SIZE))
        #render mana cost and name
        pygame.draw.circle(surface,MANA_COLOR,
            position + Vector(MANA_RADIUS+MARGIN_SIZE//2,MANA_RADIUS+MARGIN_SIZE//2),MANA_RADIUS)
        cost = self.titleFont.render(str(cardData.cost),False,(0,0,0))
        surface.blit(cost,position + (Vector(MARGIN_SIZE//2 + MANA_RADIUS,MARGIN_SIZE//2 +MANA_RADIUS) - Vector(*cost.get_rect().size)/2).toInt())
        name = self.titleFont.render(cardData.name,True,(0,0,0))
        surface.blit(name,position + Vector(MARGIN_SIZE + MANA_RADIUS*2,MARGIN_SIZE//2))
        #Text Box
        consumedH = MARGIN_SIZE*2 + TITLE_SIZE + IMAGE_H
        boxRect = (*(Vector(MARGIN_SIZE,consumedH)+position).toInt(),CARD_W-2*MARGIN_SIZE,CARD_H-consumedH-MARGIN_SIZE)
        pygame.draw.rect(surface, TEXTBOX_COLOR, boxRect)

        writeText((self.textFont,self.boldFont,self.italicFont),surface,cardData.text,pygame.rect.Rect(boxRect))

        if cardData.showTooltips:
            y = position.y
            x = position.x + CARD_W + MARGIN_SIZE*1
            self.drawTooltips(surface,x,y,cardData.tooltips)


    def drawTooltips(self,surface,x,y,tooltips):
        for tooltip in tooltips:
            rect = (x,y,TOOLTIP_W,TOOLTIP_H)
            pygame.draw.rect(surface,TOOLTIP_COLOR,rect)
            writeText((self.textFont,self.boldFont,self.italicFont),surface,tooltip,pygame.rect.Rect(rect))
            y += TOOLTIP_H + MARGIN_SIZE

    def drawHand(self,surface,cards,skips=[],draw=True,highlights = [],hover = [],**ignore):
        start = SCREEN_W/2 - ((CARD_W + MARGIN_SIZE) * len(cards) - MARGIN_SIZE)/2
        rects = [None for i in range(len(cards))]
        for test in (False,True):
            position = Vector(start,HAND_H)
            n = 0
            for card in cards:
                card.highlight = card in highlights
                card.showTooltips = card in hover
                if (card in hover) == test:
                    rects[n]  = (*position,CARD_W,CARD_H)
                    if n not in skips and draw:
                        self.draw(surface,position,card)
                n += 1
                position += Vector(MARGIN_SIZE+CARD_W,0)
        return rects

    def drawMana(self,surface,state):
        pygame.draw.circle(surface,MANA_COLOR,
            Vector(MANA_X,MANA_Y),MANA_RADIUS*2)
        mana = self.titleFont.render(str(state.mana),True,(0,0,0))
        surface.blit(mana,(Vector(MANA_X,MANA_Y) - Vector(*mana.get_rect().size)/2).toInt())

    def drawIconCount(self,surface,image,n,x,y):
        icon = loader.get_image_size(image,(ICON_SIZE,ICON_SIZE))
        surface.blit(icon,(x,y))
        if n != None:
            txt = self.titleFont.render(str(n),True,(0,0,0))
            surface.blit(txt,Vector(x + ICON_SIZE + MARGIN_SIZE/2,y + ICON_SIZE/2 - txt.get_rect().h/2).toInt())
        return (x,y,ICON_SIZE,ICON_SIZE)

    def drawDecks(self,surface,state):
        rects = {}
        data = [("assets/deck.png",state.deck,DECK_X,DECK_Y,Zone.DECK),
                ("assets/stock.png",state.stock,STOCK_X,STOCK_Y,Zone.STOCK),
                ("assets/discard.png",state.discard,DISCARD_X,DISCARD_Y,Zone.DISCARD)]
        for (image,collection,x,y,which) in data:
            rects[which] = self.drawIconCount(surface,image,len(collection),x,y)
        return rects

    def drawPlayerHealth(self,surface,health):
        self.drawIconCount(surface,"assets/heart.png",health,HEALTH_X,HEALTH_Y)

    def drawExitViewer(self,surface):
        icon = loader.get_image_size("assets/exit.png",(ICON_SIZE,ICON_SIZE))
        surface.blit(icon,(MARGIN_SIZE,MARGIN_SIZE))
        return (MARGIN_SIZE,MARGIN_SIZE,ICON_SIZE,ICON_SIZE)

    def drawCardPile(self,surface,cards,which,scroll,hover=[],choose=False):
        #render title and subtitle
        ttext = TITLE_STRINGS[which]
        if choose:
            ttext = "Choose a card from your " + ttext
        title = self.bigTitleFont.render(ttext,True,(0,0,0))
        surface.blit(title,(SCREEN_W//2 - title.get_rect().w //2,MARGIN_SIZE*2+ICON_SIZE))
        textRect = pygame.rect.Rect(0,MARGIN_SIZE*3 + ICON_SIZE + BIG_TITLE_SIZE,SCREEN_W,SCREEN_H)
        writeText((self.titleFont,self.boldTitleFont,self.italicTitleFont),surface,SUB_STRINGS[which],textRect)
        #render scrollbar
        n_rows = math.ceil(len(cards)/ROW_SIZE)
        scroll = min(max(0,n_rows-1),max(0,scroll))

        startX = SCREEN_W/2 - ROW_WIDTH/2
        startY = MARGIN_SIZE*4 + ICON_SIZE + BIG_TITLE_SIZE + TITLE_SIZE*2
        barH = SCREEN_H - startY - MARGIN_SIZE
        pygame.draw.rect(surface,SCROLLBAR_COLOR,(SCREEN_W-MARGIN_SIZE-SCROLLBAR_W,startY,SCROLLBAR_W,barH))
        buttonSize = barH//max(1,n_rows)
        pygame.draw.rect(surface,SCROLLBAR_BUTTON_COLOR,(SCREEN_W-MARGIN_SIZE-SCROLLBAR_W,startY + scroll*buttonSize,SCROLLBAR_W,buttonSize))

        cards = cards[scroll*ROW_SIZE:]

        rects = []
        for test in (False,True):
            position = Vector(startX,startY)
            rowCounter = 0
            for card in cards:
                card.showTooltips = card in hover
                if (card in hover) == test:
                    self.draw(surface,position,card)
                rects.append(((*position,CARD_W,CARD_H),card))
                position.x += CARD_W + MARGIN_SIZE*2
                rowCounter += 1
                if rowCounter == ROW_SIZE:
                    position.y += CARD_H + MARGIN_SIZE*2
                    position.x = startX
                    rowCounter = 0
                if position.y >= (SCREEN_H - CARD_H):
                    break
        return rects

    def drawEnemies(self,surface,enemies,draw=True,skipEnemies=[],enemyhover=[],skipEnemyIcons=[],**kwargs):
        rects = []
        width = sum(map(lambda x:x.width(),enemies)) + MARGIN_SIZE*2*(len(enemies) -1)
        x = SCREEN_W/2 - width/2
        centerY = MARGIN_SIZE*20 #TODO CHANGE ME.
        n = 0
        for enemy in enemies:
            rects.append((x,centerY - enemy.height()/2,enemy.width(),enemy.height()))
            if draw and (n not in skipEnemies):
                surface.blit(enemy.image,Vector(x,centerY - enemy.height()/2).toInt())
                self.drawIconCount(surface,"assets/heart.png",enemy.health(),x + enemy.width() + MARGIN_SIZE,centerY + enemy.height()/2 - ICON_SIZE)
                if n not in skipEnemyIcons:
                    self.drawIconCount(surface,enemy.intent.icon(),enemy.intent.number(),x + enemy.width()/2 - MARGIN_SIZE/2,centerY - enemy.height()/2 - ICON_SIZE - MARGIN_SIZE)
            x += enemy.width() + MARGIN_SIZE*2
            n += 1
        for index in enemyhover:
            self.drawTooltips(surface,rects[index][0] + rects[index][2] + MARGIN_SIZE,rects[index][1],enemies[index].get_tooltips())
        return rects

    def drawRunes(self,surface,runes,draw=True,skipRunes=[],runehover=[],**ignore):
        rects = []
        width = sum(map(lambda x:x.rune_image().get_rect().w,runes)) + MARGIN_SIZE*2*(len(runes) -1)
        x = SCREEN_W/2 - width/2
        centerY = SCREEN_H - CARD_H - MARGIN_SIZE * 10
        n = 0
        for rune in runes:
            W = rune.rune_image().get_rect().w
            H = rune.rune_image().get_rect().h
            rects.append((x,centerY - W/2,W,H))
            if draw and (n not in skipRunes):
                surface.blit(rune.rune_image(),Vector(x,centerY - W/2))
            x += W+ MARGIN_SIZE*2
            n += 1
        for index in runehover:
            self.drawTooltips(surface,rects[index][0] + rects[index][2] + MARGIN_SIZE,rects[index][1],runes[index].rune_tooltips)
        return rects

    def drawEndButton(self,surface):
        rect = pygame.rect.Rect(SCREEN_W - MARGIN_SIZE - END_BUTTON_W,END_BUTTON_Y - END_BUTTON_H,END_BUTTON_W,END_BUTTON_H)
        pygame.draw.rect(surface,END_BUTTON_COLOR,rect)
        s2 = self.titleFont.render("End Turn",True,(0,0,0))
        surface.blit(s2,(rect.x + rect.w /2 - s2.get_rect().w/2, rect.y + rect.h/2 - TITLE_SIZE/2))
        return rect

    def drawDeckChooser(self,surface,decks,hover=[],clicked=[]):
        writeText((self.bigTitleFont,),surface,"Choose your class.",pygame.rect.Rect(0,0,SCREEN_W,SCREEN_H))
        rects = []
        n = 0
        y = BIG_TITLE_SIZE + MARGIN_SIZE*5
        for deck in decks:
            x = MARGIN_SIZE*7
            color = (0,0,0)
            if n in hover:
                color = (0,255,0)
            if n in clicked:
                color = (255,255,0)
            name = self.titleFont.render(deck.name,True,color)
            surface.blit(name,(x,y))
            x += name.get_rect().w + MARGIN_SIZE*2
            self.drawIconCount(surface,deck.image,None,x,y)
            x += MARGIN_SIZE*2 + ICON_SIZE
            blurb = self.titleFont.render(deck.blurb,True,color)
            surface.blit(blurb,(x,y))

            x += blurb.get_rect().w
            rects.append((MARGIN_SIZE*7,y,x-MARGIN_SIZE*7,ICON_SIZE))
            y += ICON_SIZE + MARGIN_SIZE*5
            n+=1

        rect = pygame.rect.Rect(STARTBUTTON_X,STARTBUTTON_Y,STARTBUTTON_W,STARTBUTTON_H)
        pygame.draw.rect(surface,END_BUTTON_COLOR,rect)
        s2 = self.titleFont.render("Begin Game",True,(0,0,0) if len(clicked) == 0 else (255,255,0))
        surface.blit(s2,(rect.x + rect.w /2 - s2.get_rect().w/2, rect.y + rect.h/2 - TITLE_SIZE/2))

        rect2 = pygame.rect.Rect(BACKBUTTON_X,STARTBUTTON_Y,STARTBUTTON_W,STARTBUTTON_H)
        pygame.draw.rect(surface,END_BUTTON_COLOR,rect2)
        s2 = self.titleFont.render("Back",True,(0,0,0))
        surface.blit(s2,(rect2.x + rect.w /2 - s2.get_rect().w/2, rect.y + rect.h/2 - TITLE_SIZE/2))

        return (rects,rect,rect2)

    def drawPauseMenu(self,surface,hover=[]):
        writeText((self.bigTitleFont,),surface,"Paused.",pygame.rect.Rect(0,0,SCREEN_W,SCREEN_H))
        y = 0
        rects = []
        strings = ["Return to game.","Forfeit & Reselect Class.","Quit game."]
        i = 0
        for x in strings:
            y += BIG_TITLE_SIZE + MARGIN_SIZE*10
            s2 = self.bigTitleFont.render(x,True,(0,0,0) if i not in hover else (255,255,0))
            rect = s2.get_rect()
            surface.blit(s2,(SCREEN_W/2 - rect.w/2,y))
            rects.append(pygame.rect.Rect(SCREEN_W/2 - rect.w/2,y,rect.w,rect.h))
            i += 1
        return rects

    def drawTitleScreen(self,surface,hover=[]):
        writeText((self.massiveTitleFont,),surface,"LIB SLAYER 9001",pygame.rect.Rect(0,0,SCREEN_W,SCREEN_H))
        y = 0
        rects = []
        strings = ["Begin Game","Credits","Quit game"]
        i = 0
        for x in strings:
            y += BIG_TITLE_SIZE + MARGIN_SIZE*10
            s2 = self.bigTitleFont.render(x,True,(0,0,0) if i not in hover else (255,255,0))
            rect = s2.get_rect()
            surface.blit(s2,(SCREEN_W/2 - rect.w/2,y))
            rects.append(pygame.rect.Rect(SCREEN_W/2 - rect.w/2,y,rect.w,rect.h))
            i += 1
        return rects

    def drawCreditsScreen(self,surface,hover=[]):
        writeText((self.bigTitleFont,),surface,"Credits!!!",pygame.rect.Rect(0,0,SCREEN_W,SCREEN_H))
        credits = "Programming & Design - Thomas Neill \n Art Assets - Internet \n Playtesting - You :)"
        writeText((self.bigTitleFont,),surface,credits,pygame.rect.Rect(0,BIG_TITLE_SIZE + MARGIN_SIZE*10,SCREEN_W,SCREEN_H))
        rect2 = pygame.rect.Rect(BACKBUTTON_X,STARTBUTTON_Y,STARTBUTTON_W,STARTBUTTON_H)
        pygame.draw.rect(surface,END_BUTTON_COLOR,rect2)
        s2 = self.titleFont.render("Back",True,(0,0,0))
        surface.blit(s2,(rect2.x + rect2.w /2 - s2.get_rect().w/2, rect2.y + rect2.h/2 - TITLE_SIZE/2))
        return rect2
