import pygame

class ImageLoader:
    def __init__(self):
        self.dict = {}
    def get_image(self,name):
        if name not in self.dict:
            self.dict[name] = pygame.image.load(name)
        return self.dict[name]
    def get_image_size(self,name,size):
        if (name,size) not in self.dict:
            self.dict[(name,size)] = pygame.transform.scale(pygame.image.load(name),size)
        return self.dict[(name,size)]

loader = ImageLoader()
