import pygame
from GlobalGameManager import SubManager
import math

class Sprite:
	def __init__(self, app):
		self.app = app
		self.x = 0
		self.y = 0
		self.frames = []
		self.current_frame = 0
		self.size = (1, 1)
		self.rect = pygame.Rect(self.x, self.y, *self.size)
	def move(self, x, y, dt):
		# don't let the player move more than 1 tile/frame
		self.x += x
		self.y += y
	def draw(self):
		size = self.size[0] * self.app.data.manager.tiles.tile_size, self.size[1] * self.app.data.manager.tiles.tile_size
		pos = self.app.data.manager.camera.get_from_world(self.x , self.y)
		self.app.data.manager.window.draw(
			pygame.transform.scale(self.frames[int(self.current_frame)], (size[0], size[1])),
			(pos[0] - size[0] / 2, pos[1] - size[1] / 2)
		)
	def colliding(self, filter = [15], pos = None):
		if pos == None:
			pos = (self.x, self.y)
		# get the tile the sprite is on
		tile = self.app.data.manager.tiles.get_tile(math.floor(pos[0]), math.floor(pos[1]))["id"]
		# check if the tile is in the filter
		if tile in filter:
			return False
		else:
			return True
		
	def update(self, keys, dt):
		pass

class Player(Sprite):
	def __init__(self, app):
		super().__init__(app)
		self.size = (1, 1)
		self.speed = 0.02
		surface: pygame.Surface = self.app.data.manager.window.load_image("tile_sets/Slime.png")
		self.frames.append(surface.subsurface((0 * 16, 0 * 16), (16, 16)))
		self.frames.append(surface.subsurface((1 * 16, 0 * 16), (16, 16)))
		self.frames.append(surface.subsurface((2 * 16, 0 * 16), (16, 16)))
		self.frames.append(surface.subsurface((3 * 16, 0 * 16), (16, 16)))
		self.frames.append(surface.subsurface((4 * 16, 0 * 16), (16, 16)))
		self.animation = "idle"
		self.frame = 0
		self.camera_pos = [0, 0]
		self.animation_data = {
			"idle": {
				"direction": 1
			}
		}
		self.vx = 0
		self.vy = 0

	def update(self, keys, dt):
		# center the camera on the player
		last_pos = (self.x, self.y)
		if keys[pygame.K_w]:
			self.vy -= self.speed
		if keys[pygame.K_s]:
			self.vy += self.speed
		self.move(0, self.vy, dt)
		if self.colliding(pos = (self.x, self.y + 0.3125)):
			self.y = last_pos[1]
			self.vy = 0
		if keys[pygame.K_a]:
			self.vx -= self.speed
		if keys[pygame.K_d]:
			self.vx += self.speed
		self.move(self.vx, 0, dt)
		if self.colliding(pos = (self.x, self.y + 0.3125)):
			self.x = last_pos[0]
			self.vx = 0
		self.vx = 0
		self.vy = 0
		self.animate(dt)
		x, y = self.app.data.manager.mouse.tile_position
		x1, y1 = self.x - last_pos[0] / 4, self.y - last_pos[1] / 4
		self.camera_pos[0] += ((((x + self.x) / 4) + self.x / 2) - self.camera_pos[0]) / self.app.data.manager.options["camera_drag"]
		self.camera_pos[1] += ((((y + self.y) / 4) + self.y / 2) - self.camera_pos[1]) / self.app.data.manager.options["camera_drag"]
		self.app.data.manager.camera.focus(*self.camera_pos)
	def animate(self, dt):
		f = self.frame
		self.frame += dt / 200
		if int(f) == int(self.frame):
			return
		if self.animation == "idle":
			if int(self.current_frame) <= 2:
				self.current_frame += 1
				self.animation_data["idle"].update({"direction": 1})
				return
			if self.current_frame <= 2:
				self.animation_data["idle"].update({"direction": 1})
			elif int(self.current_frame) >= 4:
				self.current_frame -= 1
				self.animation_data["idle"].update({"direction": -1})
				return
			else:
				self.current_frame += self.animation_data["idle"]["direction"]
				return

class SpriteManager(SubManager):
	def __init__(self, app):
		super().__init__(app, 'sprites')
		self.app = app
		self.sprites = []
		self.Player = Player
		
	def new_sprite(self, sprite_name):
		if sprite_name in self.__dict__:
			s = self.__dict__[sprite_name](self.app)
			self.sprites.append(s)
			return s
		else:
			raise KeyError(f'Sprite \'{sprite_name}\' does not exist')
	def update(self, keys, dt):
		for sprite in self.sprites:
			sprite.update(keys, dt)
	def draw(self):
		for sprite in self.sprites:
			sprite.draw()
	def get_sprite_name(self, sprite):
		return sprite.__class__.__name__

