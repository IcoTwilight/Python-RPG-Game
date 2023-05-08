import pygame
import threading
import GlobalGameManager
import sys
from Connections import Server, Client
from rule_editor import RuleEditor
import cProfile
import UI


class Data:
	def __init__(self, **kwargs):
		self.__data = kwargs.copy()
		self.__lock = threading.Lock()
	def __getattr__(self, name):
		if name == "_Data__data" or name == "_Data__lock":
			return self.__dict__[name]
		value = self.__data[name]
		return value
	def __setattr__(self, name, value):
		if name == "_Data__data" or name == "_Data__lock":
			self.__dict__[name] = value
		else:
			self.__lock.acquire()
			self.__data[name] = value
			self.__lock.release()

class App:
	def __init__(self):
		self.data = Data(menu = "main")
		GlobalGameManager.Manager(self)
		self.data.manager.tiles.load_tiles("tile_sets/Grasslands.png")
		self.data.running = True
		self.data.player = self.data.manager.sprites.new_sprite("Player")
		self.main_menu()
		self.run()
	def run(self):
		profiler = cProfile.Profile()
		profiler.enable()  # Start profiling
		self.data.manager.tiles.load("level.data")
		self.data.player.x, self.data.player.y = self.data.manager.tiles.world_data["player_position"]
		# fix the window size when the game starts
		self.data.manager.window.resize(self.data.manager.window.width, self.data.manager.window.height)
		while self.data.running:
			# set the caption to the current fps
			pygame.display.set_caption("FPS: " + str(self.data.manager.window.clock.get_fps()))
			self.data.manager.events()
			self.data.manager.camera.get_on_screen()
			self.data.manager.tiles.draw()
			self.data.manager.sprites.draw()
			self.data.manager.window.update()
			self.data.manager.window.draw_text(str((self.data.player.x, self.data.player.y)), (0, 0, 0), (0, 0))
			self.data.manager.mouse.draw()
			self.data.manager.window.render()
		"""if self.data.connectionEstablished:
			self.data.connection.close()
			if self.data.manager.connection.type == "server":
				self.data.manager.tiles.save("level.data")"""
		self.data.manager.tiles.save("level.data")


		profiler.disable()  # Stop profiling
		profiler.print_stats(sort="cumtime")  # Print the profiling results sorted by cumulative time
		pygame.quit()
		sys.exit()
	def main_menu(self):
		# create a button called "Play" and set it's position to the top left of the screen
		all = []
		button_width = 100
		button_height = 50
		#
		play_button = 		UI.Button(10, ((button_height + 10) * 0) + 10, button_width, button_height, "Play")
		#
		new_game_button = 		UI.Button(10, ((button_height + 10) * 0) + 10, button_width, button_height, "New Game")
		load_game_button = 		UI.Button(10, ((button_height + 10) * 1) + 10, button_width, button_height, "Load Game")
		back_button = 		UI.Button(10, ((button_height + 10) * 2) + 10, button_width, button_height, "Back")
		all.extend([play_button, new_game_button, load_game_button, back_button])
		#
		multiplayer_button = 	UI.Button(10, ((button_height + 10) * 1) + 10, button_width, button_height, "Multiplayer")
		#
		host_button = 		UI.Button(10, ((button_height + 10) * 0) + 10, button_width, button_height, "Host")
		join_button = 		UI.Button(10, ((button_height + 10) * 1) + 10, button_width, button_height, "Join")
		all.extend([multiplayer_button, host_button, join_button])
		#
		options_button = 		UI.Button(10, ((button_height + 10) * 2) + 10, button_width, button_height, "options")
		#
		mouse_drag_slider = 	UI.Slider(10, ((button_height + 10) * 0) + 10, button_width, button_height, 1, 100)
		camera_drag_slider = 	UI.Slider(10, ((button_height + 10) * 1) + 10, button_width, button_height, 1, 100)
		self.data.manager.options.load()
		mouse_drag_slider.value = self.data.manager.options.get("mouse_drag")
		camera_drag_slider.value = self.data.manager.options.get("camera_drag")

		all.extend([options_button, mouse_drag_slider, camera_drag_slider])
		#
		developer_button = 		UI.Button(10, ((button_height + 10) * 3) + 10, button_width, button_height, "Developer")
		#
		rule_editor_button = 	UI.Button(10, ((button_height + 10) * 0) + 10, button_width, button_height, "Rule Editor")
		visual_tile_ids_button = 	UI.Button(10, ((button_height + 10) * 1) + 10, button_width, button_height, "Visual Tile IDs")
		all.extend([developer_button, rule_editor_button, visual_tile_ids_button])
		quit_button = 		UI.Button(10, ((button_height + 10) * 4) + 10, button_width, button_height, "Quit")
		all.append(quit_button)
		self.data.main_menu = "main"
		while(1):
			for element in all:
				element.size.x = self.data.manager.window.width - 20
				element.rect.w = self.data.manager.window.width - 20
			self.data.manager.window.update()
			keys_just_pressed = []
			mouse_just_pressed = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False}
			mouse_just_released = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False}
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.data.running = False
					return
				if event.type == pygame.KEYDOWN:
					keys_just_pressed.append(event.key)
				elif event.type==pygame.MOUSEBUTTONDOWN:
					mouse_just_pressed[event.button - 1] = True
				elif event.type==pygame.MOUSEBUTTONUP:
					mouse_just_released[event.button - 1] = True
			self.data.manager.mouse.update(mouse_just_pressed, mouse_just_released)
			mouse_position = self.data.manager.mouse.position
			if self.data.main_menu == "main":
				play_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				multiplayer_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				options_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				developer_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				quit_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				if play_button.clicked:
					self.data.main_menu = "play"
				elif multiplayer_button.clicked:
					self.data.main_menu = "multiplayer"
				elif options_button.clicked:
					self.data.main_menu = "options"
				elif developer_button.clicked:
					self.data.main_menu = "developer"
				elif quit_button.clicked:
					self.data.running = False
					return
			
			elif self.data.main_menu == "play":
				new_game_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				load_game_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				back_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				if new_game_button.clicked:
					self.data.main_menu = "new game"
				elif load_game_button.clicked:
					self.data.main_menu = "load game"
				elif back_button.clicked:
					self.data.main_menu = "main"

			elif self.data.main_menu == "multiplayer":
				host_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				join_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				back_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				if host_button.clicked:
					self.data.main_menu = "host"
				elif join_button.clicked:
					self.data.main_menu = "join"
				elif back_button.clicked:
					self.data.main_menu = "main"
			
			elif self.data.main_menu == "options":
				mouse_drag_slider.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				camera_drag_slider.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				back_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				self.data.manager.options.set("mouse_drag", mouse_drag_slider.value)
				self.data.manager.options.set("camera_drag", camera_drag_slider.value)
				if back_button.clicked:
					self.data.main_menu = "main"
					self.data.manager.options.save()
			
			elif self.data.main_menu == "developer":
				rule_editor_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				visual_tile_ids_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				back_button.draw(self.data.manager.window.display, mouse_just_pressed, mouse_position)
				if rule_editor_button.clicked:
					self.data.main_menu = "rule editor"
				elif visual_tile_ids_button.clicked:
					self.data.main_menu = "visual tile ids"
				elif back_button.clicked:
					self.data.main_menu = "main"
			
			elif self.data.main_menu == "new game":
				self.data.manager.generate.new_world()
				return
			
			elif self.data.main_menu == "load game":
				return
			
			elif self.data.main_menu == "host":
				self.data.main_menu = "multiplayer"
			
			elif self.data.main_menu == "join":
				self.data.main_menu = "multiplayer"
			
			elif self.data.main_menu == "rule editor":
				r = RuleEditor(self)
				self.data.main_menu = "developer"
			
			elif self.data.main_menu == "visual tile ids":
				self.data.main_menu = "developer"

			
			
			self.data.manager.mouse.draw()
			self.data.manager.window.render()
			

		

if __name__ == "__main__":
	App()