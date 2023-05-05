import pygame
from pygame.locals import *

class Window:
	def __init__(self, width, height, title):
		self.width = width
		self.height = height
		self.title = title
		self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont("Consolas", 12)
	@property.getter
	def width(self):
		return pygame.display.get_surface().get_width()
	@property.getter
	def height(self):
		return pygame.display.get_surface().get_height()
	@property.getter
	def title(self):
		return pygame.display.get_caption()[0]
	@property.setter
	def title(self, title):
		pygame.display.set_caption(title)
	@property.setter
	def width(self, width):
		self.screen = pygame.display.set_mode((width, self.height))
	@property.setter
	def height(self, height):
		self.screen = pygame.display.set_mode((self.width, height))
	def update(self):
		pygame.display.update()
		self.clock.tick(60)
	def clear(self, color = (0, 0, 0)):
		self.screen.fill(color)
	def draw(self, surface, position):
		self.screen.blit(surface, position)
	def draw_text(self, text, color, position):
		self.screen.blit(self.font.render(text, True, color), position)
	def load_image(self, path):
		return pygame.image.load(path).convert_alpha()