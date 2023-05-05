# this file is an editor for the rules of how tiles fit together
# it is a simple ui that allows you to draw paths over the tiles
# and then calculate the rules from that and save them to a file
import pygame

class RuleEditor:
	def __init__(self, app):
		self.app = app
		self.screen = self.app.data.manager.window.display
		self.running = True
		self.kill = False
		self.tile_sets = {}
		self.tile_rules = {}
		self.current_tile = 0
		self.set_layer = 0
		self.top_center = pygame.Rect(64, 0, 64, 64)
		self.top_right = pygame.Rect(128, 0, 64, 64)
		self.center_right = pygame.Rect(128, 64, 64, 64)
		self.bottom_right = pygame.Rect(128, 128, 64, 64)
		self.bottom_center = pygame.Rect(64, 128, 64, 64)
		self.bottom_left = pygame.Rect(0, 128, 64, 64)
		self.center_left = pygame.Rect(0, 64, 64, 64)
		self.top_left = pygame.Rect(0, 0, 64, 64)
		# open the tile_rules.data file and load the rules
		with open("tile_rules.data", "r") as file:
			t = self.app.data.manager.methods.load_dict(file.read())
			self.tile_rules = t.get("tile_rules", [{}])
			self.tile_sets = t.get("tile_sets", [[]])

		while(self.running):
			if self.update() == False:
				self.kill = True
				break
			else:
				self.kill = False
			self.draw()
	
	def update(self):
		self.app.data.manager.mouse.update([], [])
		mouse_x, mouse_y = self.app.data.manager.mouse.position
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				self.app.running = False
				with open("tile_rules.data", "w") as file:
					file.write(self.app.data.manager.methods.stringify_dict({"tile_rules": self.tile_rules, "tile_sets": self.tile_sets}))
				return False # kill the entire game
			if event.type == pygame.MOUSEBUTTONDOWN:
				if   self.top_center.collidepoint(mouse_x, mouse_y):    self.itter_rule(self.current_tile, 0)
				elif self.top_right.collidepoint(mouse_x, mouse_y):     self.itter_rule(self.current_tile, 1)
				elif self.center_right.collidepoint(mouse_x, mouse_y):  self.itter_rule(self.current_tile, 2)
				elif self.bottom_right.collidepoint(mouse_x, mouse_y):  self.itter_rule(self.current_tile, 3)
				elif self.bottom_center.collidepoint(mouse_x, mouse_y): self.itter_rule(self.current_tile, 4)
				elif self.bottom_left.collidepoint(mouse_x, mouse_y):   self.itter_rule(self.current_tile, 5)
				elif self.center_left.collidepoint(mouse_x, mouse_y):   self.itter_rule(self.current_tile, 6)
				elif self.top_left.collidepoint(mouse_x, mouse_y):      self.itter_rule(self.current_tile, 7)

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					self.current_tile -= 1
					if self.current_tile < 0:
						self.current_tile = len(self.app.data.manager.tiles.stored_tiles) - 1
						if self.current_tile < 0:
							self.current_tile = 0
				if event.key == pygame.K_RIGHT:
					self.current_tile += 1
					if self.current_tile >= len(self.app.data.manager.tiles.stored_tiles):
						self.current_tile = 0
						if self.current_tile >= len(self.app.data.manager.tiles.stored_tiles):
							self.current_tile = len(self.app.data.manager.tiles.stored_tiles) - 1
				if event.key == pygame.K_SPACE:
					if self.current_tile in self.tile_sets[self.set_layer]:
						self.tile_sets[self.set_layer].remove(self.current_tile)
					else:
						self.tile_sets[self.set_layer].append(self.current_tile)

	def itter_rule(self, id, rule):
		# get the rules for the tile
		rules = self.get_rules(id)
		# get the rule we want to change
		r = rules[rule]
		# if the rule is false, make it true
		if r == False:
			r = True
		# if the rule is true, make it None
		elif r == True:
			r = None
		# if the rule is None, make it False
		elif r == None:
			r = False
		# return the new rule
		self.set_rule(id, rule, r)

	def draw(self):
		self.screen.fill((20,100,20) if self.current_tile in self.tile_sets[self.set_layer] else (100,20,20))
		width = 14
		font = pygame.font.SysFont("consolas", 64//2)
		image = self.app.data.manager.tiles.stored_tiles[self.current_tile]
		image = pygame.transform.scale(image["image"], (64, 64))
		self.screen.blit(image, (64, 64))
		# now we draw the rules around it.
		rules = self.get_rules(self.current_tile)
		colors = {
			True: (100,200,100),
			False: (200,100,100),
			None: (100,100,200)
		}
		pygame.draw.rect(self.screen, colors[rules[0]], self.top_center)
		pygame.draw.rect(self.screen, colors[rules[1]], self.top_right)
		pygame.draw.rect(self.screen, colors[rules[2]], self.center_right)
		pygame.draw.rect(self.screen, colors[rules[3]], self.bottom_right)
		pygame.draw.rect(self.screen, colors[rules[4]], self.bottom_center)
		pygame.draw.rect(self.screen, colors[rules[5]], self.bottom_left)
		pygame.draw.rect(self.screen, colors[rules[6]], self.center_left)
		pygame.draw.rect(self.screen, colors[rules[7]], self.top_left)

		# now we draw the text
		text = font.render("Current Tile ID:" + str(self.current_tile), True, (255,255,255))
		self.screen.blit(text, (128, 20))

		self.app.data.manager.mouse.draw(self.screen)
		
		pygame.display.flip()


	
	def get_rules(self, id: int) -> list:
		# get the rules for a tile
		if id not in self.tile_rules[self.set_layer]:
			self.tile_rules[self.set_layer][self.current_tile] = [True, True, True, True, True, True, True, True].copy()
		return self.tile_rules[self.set_layer][self.current_tile]
	
	def set_rule(self, id: int, rule: int, value: bool) -> None:
		# set a rule for a tile
		rules = self.get_rules(id)
		rules[rule] = value