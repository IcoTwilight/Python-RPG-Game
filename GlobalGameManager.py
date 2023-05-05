import threading
import pygame
import ast
import noise
import random
import math
import threading
import numpy as np

class SubManager:
	def __init__(self, app, name: str):
		self.app = app
		self.app.data.manager.add_submanager(name, self)
		self.name = name
		self.lock = threading.Lock()

class TilesManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "tiles")
		self.tiles = {}
		self.tile_size = 128
		self.stored_tiles = []
		self.stored_tiles_size = 16
		self.world_seed = random.randrange(0, 1000000)
		self.size_cache = {}
		self.tile_sets = 	None
		self.type_rules = 	None
		self.default_tile_application = 24
		self.world_generation_depth = 1
		# load the tile_rules from the tile_rules.data file
		with open("tile_rules.data", "r") as file:
			data = file.read()
			data = self.app.data.manager.methods.load_dict(data)
			self.tile_sets = data["tile_sets"]
			self.type_rules = data["tile_rules"]
			print(self.tile_sets)
			print(self.type_rules)
	def set_tile(self, x: int, y: int, tile: dict, send = True, apply = False, depth = 2) -> None:
		self.lock.acquire()
		self.tiles[(math.floor(x), math.floor(y))] = tile
		self.lock.release()
		if apply:
			self.apply_rules(x, y, depth)
		"""if send:
			self.app.data.manager.connection.send({"type": "set_tiles", "positions": [(x, y)], "tiles": [tile]})"""
	def get_tile(self, x: int, y: int, apply_rules = True) -> dict:
		tile = self.tiles.get((math.floor(x), math.floor(y)), None)
		if tile is None:
			tile = self.app.data.manager.generate.tile(x, y, self.world_seed)
			if apply_rules:
				self.tiles[(x, y)] = tile
				self.apply_rules(x, y, self.world_generation_depth)
		return tile
	def apply_rules(self, x: int, y: int, depth = 2) -> None:
		# construct the recipe for the tile
		tile = self.get_tile(x, y, False)
		rule_id = None
		if tile is None:
			return
		for _tile_set in self.tile_sets:
			if tile["id"] in _tile_set:
				tile_set = _tile_set
				rule_id = self.tile_sets.index(_tile_set)
				break
		if rule_id is not None:
			if tile["id"] in self.type_rules[rule_id]:

				recipe = []
				recipe.append(self.get_tile(x, y - 1, False)["id"] in self.tile_sets[rule_id]) # up
				recipe.append(self.get_tile(x + 1, y - 1, False)["id"] in self.tile_sets[rule_id]) # up right
				recipe.append(self.get_tile(x + 1, y, False)["id"] in self.tile_sets[rule_id]) # right
				recipe.append(self.get_tile(x + 1, y + 1, False)["id"] in self.tile_sets[rule_id]) # down right
				recipe.append(self.get_tile(x, y + 1, False)["id"] in self.tile_sets[rule_id]) # down
				recipe.append(self.get_tile(x - 1, y + 1, False)["id"] in self.tile_sets[rule_id]) # down left
				recipe.append(self.get_tile(x - 1, y, False)["id"] in self.tile_sets[rule_id]) # left
				recipe.append(self.get_tile(x - 1, y - 1, False)["id"] in self.tile_sets[rule_id]) # up left

				# loop over all the rules
				for key, value in self.type_rules[rule_id].items():
					# loop over the recipe and the value
					for r, v in zip(recipe, value):
						# if the value is None, skip it as we don't care about it
						if v == None:
							continue
						# if the recipe doesn't match the value, break
						if r != v:
							break
					else:
						# if the recipe matches the value, set the tile to the key
						if key in self.tile_sets[rule_id]:
							self.set_tile(x, y, {"id": key}, False, False)
							break
						else:
							continue
				else:
					print("Found an invalid tile")
			

		# apply rules to the neighbours
		if depth > 0:
			self.apply_rules(x, y - 1, depth - 1)
			self.apply_rules(x + 1, y - 1, depth - 1)
			self.apply_rules(x + 1, y, depth - 1)
			self.apply_rules(x + 1, y + 1, depth - 1)
			self.apply_rules(x, y + 1, depth - 1)
			self.apply_rules(x - 1, y + 1, depth - 1)
			self.apply_rules(x - 1, y, depth - 1)
			self.apply_rules(x - 1, y - 1, depth - 1)
			

	def set_tiles(self, positions: list[tuple], tiles: list[dict], send = False) -> None:
		self.lock.acquire()
		for i in range(len(positions)):
			self.tiles[tuple(positions[i])] = tiles[i]
		self.lock.release()
		"""if send:
			self.app.data.manager.connection.send({"type": "set_tiles", "positions": positions, "tiles": tiles})"""
	def get_tiles(self, positions: list[tuple]) -> list[dict]:
		self.lock.acquire()
		tiles = []
		for position in positions:
			tiles.append(self.get_tile(position[0], position[1]))
		self.lock.release()
		return tiles
	def __repr__(self) -> str:
		return str(self.tiles)
	def __getitem__(self, key: int) -> dict:
		return self.get_tile(key)
	def get_tile_info(self, key: int) -> dict:
		return self.stored_tiles[key]
	def add_tile_info(self, tile: dict) -> None:
		self.stored_tiles.append(tile)
	def load_tiles(self, file:str) -> None:
		surface = self.app.data.manager.window.load_image(file)
		for y in range(surface.get_height() // self.stored_tiles_size):
			for x in range(surface.get_width() // self.stored_tiles_size):
				s = surface.subsurface((x * self.stored_tiles_size, y * self.stored_tiles_size, self.stored_tiles_size, self.stored_tiles_size))
				self.add_tile_info({
					"image": s,
				})
	def draw(self):
		# Use local variables and a single loop
		get_tile = self.get_tile
		scale = self.scale
		tile_size = self.tile_size
		surface = self.app.data.manager.window.screen
		gets_from_world = self.app.data.manager.camera.gets_from_world
		
		positions = np.array(self.app.data.manager.camera.tiles_on_screen)
		screen_positions = gets_from_world(positions)
		
		for i, position in enumerate(positions):
			screen_position = screen_positions[i]
			x, y = position
			image = get_tile(x, y)["id"]
			image = scale(image, tile_size)
			surface.blit(image, tuple(screen_position))



	def parrallel_get_from_world(self, x, y):
		get_from_world = self.app.data.manager.camera.get_from_world
		self.from_world[tuple((x, y))] = get_from_world(x, y)

	def scale(self, id, size):
		try:
			return self.size_cache[(id, size)]
		except:
			self.size_cache[(id, size)] = pygame.transform.scale(self.get_tile_info(id)["image"], (size // self.app.data.manager.window.display_down_size, size // self.app.data.manager.window.display_down_size)).convert_alpha()
			return self.size_cache[(id, size)]
	
	def get_all_tiles(self):
		return [self.tiles[key] for key in self.tiles]
	def get_all_positions(self):
		return [key for key in self.tiles]
	def save(self, file: str) -> None:
		with open(file, "w") as f:
			f.write(self.app.data.manager.methods.stringify_dict({"seed": self.world_seed,"tiles":self.tiles, "player_position": (self.app.data.player.x, self.app.data.player.y)}))
	def load(self, file: str) -> None:
		with open(file, "r") as f:
			self.world_data = self.app.data.manager.methods.load_dict(f.read())
			self.world_seed = self.world_data["seed"]
			self.tiles = self.world_data["tiles"]
	
	def visualize_tiles(self, surface: pygame.Surface) -> None:
		width = 14
		size = 40
		font = pygame.font.SysFont("consolas", size//2)
		for i, tile in enumerate(self.stored_tiles):
			x = (i % width) * 1.1
			y = (i // width)*1.1
			image = tile["image"]
			image = pygame.transform.scale(image, (size, size))
			surface.blit(image, (x * size, y * size))
			# draw the id
			text = font.render(str(i), True, (255, 255, 255))
			surface.blit(text, (x * size, y * size))
			

class CameraManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "camera")
		self.position = np.array([0, 0], dtype=np.float64)
		self.zoom = 128
		self.max_zoom = 128
		self.min_zoom = 4
		self.set_position(0, 0)

	def set_position(self, x: int, y: int) -> None:
		self.position = np.array([x, y], dtype=np.float64)

	def set_zoom(self, zoom: int) -> None:
		pos = self.get_from_screen(self.app.data.manager.window.width // 2, self.app.data.manager.window.height // 2)
		self.app.data.manager.tiles.tile_size = min(max(zoom, self.min_zoom), self.max_zoom)
		self.focus(*pos)

	def focus(self, x: int, y: int) -> None:
		window = self.app.data.manager.window
		tiles = self.app.data.manager.tiles
		dx = window.width / 2 - x * tiles.tile_size
		dy = window.height / 2 - y * tiles.tile_size
		self.position = np.array([dx, dy], dtype=np.float64)

	def move(self, x: int, y: int) -> None:
		self.position -= np.array([x, y], dtype=np.float64)

	def get_from_screen(self, x: int, y: int) -> np.ndarray:
		# take a space from screen space and convert it to tile space
		tiles = self.app.data.manager.tiles
		dx, dy = self.position
		screen_x = (x - dx) / tiles.tile_size
		screen_y = (y - dy) / tiles.tile_size
		return np.array([screen_x, screen_y], dtype=np.float64)

	def get_from_world(self, x: int, y: int) -> np.ndarray:
		# take a space from tile world space and convert it to screen space
		tiles = self.app.data.manager.tiles
		window = self.app.data.manager.window
		tile_size = tiles.tile_size
		display_down_size_reciprocal = 1 / window.display_down_size
		dx, dy = self.position
		#zt = zoom * tile_size
		screen_x = (x * tile_size + dx) * display_down_size_reciprocal
		screen_y = (y * tile_size + dy) * display_down_size_reciprocal
		return np.array([screen_x, screen_y], dtype=np.float64)

	def gets_from_world(self, positions: np.ndarray) -> np.ndarray:
		# take multiple positions from the world and convert them to screen space.
		tiles = self.app.data.manager.tiles
		window = self.app.data.manager.window
		tile_size = tiles.tile_size
		display_down_size_reciprocal = 1 / window.display_down_size
		dx, dy = self.position
		#zt = zoom * tile_size
		screen_positions = (positions * tile_size + np.array([dx, dy])) * display_down_size_reciprocal
		return screen_positions


	def get_on_screen(self):
		window = self.app.data.manager.window
		# get the tile position at 0, 0
		pos_0 = self.get_from_screen(0, 0)

		# get the tile position at the bottom right of the screen
		pos_br = self.get_from_screen(window.width, window.height)

		# compute the range of tile coordinates
		x_range = np.arange(np.floor(pos_0[0]), np.ceil(pos_br[0]) + 1, dtype=int)
		y_range = np.arange(np.floor(pos_0[1]), np.ceil(pos_br[1]) + 1, dtype=int)

		# create a meshgrid of tile coordinates
		xx, yy = np.meshgrid(x_range, y_range, indexing='xy')

		# flatten the meshgrid into a 1D array of tile coordinates
		coords = np.vstack((xx.flatten(), yy.flatten())).T

		self.tiles_on_screen = coords.tolist()

		return self.tiles_on_screen

class Window(SubManager):
	def __init__(self, app, width, height, title):
		super().__init__(app, "window")
		pygame.init()
		self.display = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE)
		self.display_down_size = 1 # the amount to downsize the display by when rendering
		self.screen = pygame.Surface((width // self.display_down_size, height // self.display_down_size))
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		self.dt = 0
	def update(self):
		screen = pygame.transform.scale(self.screen, (self.width, self.height))
		self.display.blit(screen, (0, 0))
	def render(self):
		pygame.display.flip()
		self.screen.fill((0, 0, 0))
		self.dt = self.clock.tick(0)
	def draw(self, surface, position):
		self.screen.blit(surface, position)
	def draw_to(self, surface, position, target_surface):
		target_surface.blit(surface, position)
	def draw_text(self, text, color, position, size = 12):
		font = pygame.font.SysFont("Consolas", size)
		surface = font.render(text, True, color)
		self.display.blit(surface, position)
		w, h = surface.copy().get_size()
		return pygame.rect.Rect(*position, w, h)
	def load_image(self, path):
		return pygame.image.load(path).convert_alpha()
	def draw_rect(self, rect, color):
		pygame.draw.rect(self.screen, color, rect)
	def compute_display_down_size(self):
		self.screen = pygame.Surface((self.width // self.display_down_size, self.height // self.display_down_size))
	width = property()
	@width.getter
	def width(self):
		return self.display.get_width()
	@width.setter
	def width(self, value):
		self.display = pygame.display.set_mode((value, self.height), pygame.RESIZABLE)
	height = property()
	@height.getter
	def height(self):
		return self.display.get_height()
	@height.setter
	def height(self, value):
		self.display = pygame.display.set_mode((self.width, value), pygame.RESIZABLE)
	def resize(self, width, height):
		self.width = width
		self.height = height
		self.compute_display_down_size()
	title = property()
	@title.getter
	def title(self):
		return pygame.display.get_caption()[0]
	@title.setter
	def title(self, value):
		pygame.display.set_caption(value)
	def get_mouse_pos(self):
		x, y = pygame.mouse.get_pos()
		x, y = x // self.display_down_size, y // self.display_down_size
		return x, y

class EventsManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "events")
	def __call__(self):
		pressed = pygame.key.get_pressed()
		just_pressed_mouse = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False}
		just_release_mouse = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False}
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.app.data.running = False
			elif event.type == pygame.VIDEORESIZE:
				self.app.data.manager.window.resize(event.w, event.h)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.app.data.running = False
				if event.key == pygame.K_s and pressed[pygame.K_LCTRL]:
					self.app.data.manager.tiles.save("level.data")
			elif event.type==pygame.MOUSEBUTTONDOWN:
				if event.button == 4:
					self.app.data.manager.camera.set_zoom(self.app.data.manager.tiles.tile_size + 1)
				elif event.button == 5:
					self.app.data.manager.camera.set_zoom(self.app.data.manager.tiles.tile_size - 1)
				just_pressed_mouse[event.button - 1] = True
			elif event.type==pygame.MOUSEBUTTONUP:
				just_release_mouse[event.button - 1] = True
		self.app.data.manager.mouse.update(just_pressed_mouse, just_release_mouse)
		if self.app.data.manager.mouse.pressed[1]:
			self.app.data.manager.camera.move(-self.app.data.manager.mouse.motion[0], -self.app.data.manager.mouse.motion[1])
		if self.app.data.manager.mouse.pressed[2]:
			self.app.data.manager.tiles.set_tile(*self.app.data.manager.mouse.tile_position, {"id": 15}, apply = True, depth = 1)
		if self.app.data.manager.mouse.pressed[0]:
			self.app.data.manager.tiles.apply_rules(*self.app.data.manager.mouse.tile_position, depth = 0)
			print(*self.app.data.manager.mouse.tile_position)
		
		self.app.data.manager.sprites.update(pressed, self.app.data.manager.window.dt)

"""class ConnectionManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "connection")
	def set_connection(self, connection) -> None:
		self.connection = connection
		self.connection.on_message = self.on_message
	def send(self, data: dict, client = None) -> None:
		if self.app.data.connectionEstablished == False:
			return
		if client is None:
			self.connection.send_message(self.app.data.manager.methods.stringify_dict(data))
		else:
			self.connection.send_message_to_client(client, self.app.data.manager.methods.stringify_dict(data))
	def on_message(self, client_socket = None, client_address = None, data = None) -> None:
		data = self.app.data.manager.methods.load_dict(data)
		print(client_socket, client_address, data)
		if "type" in data:
			if data["type"] == "set_tiles":
				self.app.data.manager.tiles.set_tiles(data["positions"], data["tiles"], False if self.app.data.connection.type == "client" else True)
				if self.app.data.connection.type == "server":
					# send to all clients
					self.send({"type": "set_tiles", "positions": data["positions"], "tiles": data["tiles"]})
			if data["type"] == "get_tiles":
				if self.app.data.connection.type == "server":
					# send the tiles to the client
					tiles = [self.app.data.manager.tiles.get_tile(x, y) for x, y in data["positions"]]
					self.send({"type": "set_tiles", "positions": data["positions"], "tiles": tiles}, client_address)"""
			

class MethodsManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "methods")
	def load_dict(self, dictionary: str):
		return ast.literal_eval(dictionary)
	def stringify_dict(self, dictionary: dict):
		return str(dictionary)

class GenerateManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "generate")
	def tile(self, x, y, seed):
		scale = 0.001
		octaves = 6
		persistence = 0.75
		lacunarity = 2.0

		# Normalize the coordinates
		x = x * scale
		y = y * scale

		# Generate Simplex noise using the seed, x, and y
		simplex_value = noise.snoise2(x, y, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=seed)

		# Convert Simplex noise to a tile index
		if simplex_value < 0.2: # water
			return {"id": 24}
		else: # stone
			return {"id": 15}
	
	def new_world(self):
		seed = random.randint(0, 1000000)
		# save the seed to a file
		with open("level.data", "w") as f:
			f.write(self.app.data.manager.methods.stringify_dict({"seed": seed, "tiles": {}, "player_position": (0, 0)}))
		# set the tiles to use the new level
		self.app.data.manager.tiles.load("level.data")

class MouseManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "mouse")
		self.position = (0, 0)
		self.tile_position = (0, 0)
		self.motion = (0, 0)
		self.pressed = (False, False, False)
		self.just_pressed = (False, False, False)
		self.just_released = (False, False, False)
		# hide the mouse:
		pygame.mouse.set_visible(False)
	def update(self, just_pressed, just_released) -> None:
		# work out the dx, du of the distance the mouse has moved
		dx = (pygame.mouse.get_pos()[0] - self.position[0])
		dy = (pygame.mouse.get_pos()[1] - self.position[1])
		# set the mouse position to the current position
		self.position = (self.position[0] + dx / self.app.data.manager.options["mouse_drag"], self.position[1] + dy / self.app.data.manager.options["mouse_drag"])
		# set the mouse motion to the current motion
		self.motion = (dx, dy)
		# set the mouse tile position to the current tile position
		self.tile_position = self.app.data.manager.camera.get_from_screen(*self.position)
		# set the mouse pressed to the current pressed
		self.pressed = pygame.mouse.get_pressed()
		# set the mouse just pressed to the current just pressed
		self.just_pressed = just_pressed
		# set the mouse just released to the current just released
		self.just_released = just_released
	def draw(self, display = None) -> None:
		if display is None:
			display = self.app.data.manager.window.display
		pygame.draw.circle(display, (200, 200, 200, 200), self.position, 5)

class OptionsManager(SubManager):
	def __init__(self, app):
		super().__init__(app, "options")
		self.options = {}
		self.load()
	def load(self):
		with open("options.data", "r") as f:
			self.options = self.app.data.manager.methods.load_dict(f.read())
	def save(self):
		with open("options.data", "w") as f:
			f.write(self.app.data.manager.methods.stringify_dict(self.options))
	def get(self, name):
		return self.options[name]
	def set(self, name, value):
		self.options[name] = value
	def __getitem__(self, name):
		return self.get(name)

class Manager:
	def __init__(self, app):
		from SpriteManager import SpriteManager
		self.app = app
		self.lock = threading.Lock()
		self.submanagers = {}
		self.app.data.manager = self
		self.methods = MethodsManager(self.app)
		self.tiles = TilesManager(self.app)
		self.camera = CameraManager(self.app)
		self.window = Window(self.app, 800, 600, "Game")
		self.events = EventsManager(self.app)
		self.sprites = SpriteManager(self.app)
		"""self.connection = ConnectionManager(self.app)"""
		self.generate = GenerateManager(self.app)
		self.mouse = MouseManager(self.app)
		self.options = OptionsManager(self.app)
	def add_submanager(self, name: str, submanager: SubManager) -> None:
		self.lock.acquire()
		self.submanagers[name] = submanager
		self.lock.release()