import pygame

class Arrow:
    def __init__(self,start):
        self.start = start
    def set_destination(self,what):
        self.destination = what
    def draw(self,surface):
        #Draw a circle trail: Maybe animate???
        delta = self.destination - self.start
        distance = delta.magnitude()
        if distance == 0:
            return
        offset = (pygame.time.get_ticks()//15) % 10
        step = delta / distance * 10
        stepper = self.start
        for i in range(int(distance//10)):
            pygame.draw.circle(surface,(255,255,255),stepper.toInt() + (step*offset/10).toInt(),3)
            stepper += step
        #Now draw a little triangle for the head of the arrow
        pygame.draw.polygon(surface,(255,255,255), [
                self.destination,
                self.destination - step + step.perpendicular(),
                self.destination - step - step.perpendicular()])
