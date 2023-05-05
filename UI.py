# this file is a module for adding UI elements into pygame games/apps

import pygame

# sub class for all UI elements
class UIElement:
	def __init__(self, x, y, w, h):
		self.position = pygame.math.Vector2(x, y)
		self.size = pygame.math.Vector2(w, h)
		self.rect = pygame.Rect(x, y, w, h)
		self.visible = True
	def draw(self, surface, keyboard_just_pressed, mouse_buttons, mouse_position):
		self.update(keyboard_just_pressed, mouse_buttons, mouse_position)
	def update(self, keyboard_just_pressed, mouse_buttons, mouse_position):
		pass

class Button(UIElement):
	def __init__(self, x, y, w, h, text = "Hello, World!", font_size = 12, color = (50, 50, 50), hover_color = (100, 100, 100), text_color = (100, 100, 100), hover_text_color = (50, 50, 50)):
		super().__init__(x, y, w, h)
		self.text = text
		self.font_size = font_size
		self.font = pygame.font.SysFont("consolas", self.font_size)
		self.color = color
		self.hover_color = hover_color
		self.text_color = text_color
		self.hover_text_color = hover_text_color
		self.hovering = False
	def draw(self, surface, mouse_buttons, mouse_position):
		if self.visible:
			self.update(mouse_buttons, mouse_position)
			if self.hovering:
				pygame.draw.rect(surface, self.hover_color, self.rect)
				text = self.font.render(self.text, True, self.hover_text_color)
			else:
				pygame.draw.rect(surface, self.color, self.rect)
				text = self.font.render(self.text, True, self.text_color)
			surface.blit(text, (self.position.x + self.size.x / 2 - text.get_width() / 2, self.position.y + self.size.y / 2 - text.get_height() / 2))
	def update(self, mouse_buttons, mouse_position):
		self.clicked = False
		if self.rect.collidepoint(mouse_position):
			self.hovering = True
			if mouse_buttons[0]:
				self.on_click()
				self.clicked = True
		else:
			self.hovering = False
	def on_click(self):
		pass
	def set_on_click(self, function):
		self.on_click = function

class Slider(UIElement):
	def __init__(self, x, y, w, h, min, max, background_color = (50, 50, 50), slider_color = (100, 100, 100), text_color = (200, 200, 200)):
		super().__init__(x, y, w, h)
		self.min = min
		self.max = max
		self.value = min
		self.background_color = background_color
		self.slider_color = slider_color
		self.text_color = text_color
	def draw(self, surface, mouse_buttons, mouse_position):
		if self.visible:
			self.update(mouse_buttons, mouse_position)
			pygame.draw.rect(surface, self.background_color, self.rect)
			pygame.draw.rect(surface, self.slider_color, pygame.Rect(self.position.x, self.position.y, self.size.x * (self.value - self.min) / (self.max - self.min), self.size.y))
			# draw value
			font = pygame.font.SysFont("consolas", 12)
			text = font.render(str(round(self.value, 2)), True, self.text_color)
			surface.blit(text, (self.position.x + self.size.x / 2 - text.get_width() / 2, self.position.y + self.size.y / 2 - text.get_height() / 2))

	def update(self, mouse_buttons, mouse_position):
		if self.rect.collidepoint(mouse_position):
			if mouse_buttons[0]:
				self.value = (mouse_position[0] - self.position.x) / self.size.x * (self.max - self.min) + self.min
				if self.value > self.max:
					self.value = self.max
				elif self.value < self.min:
					self.value = self.min
	def get_value(self):
		return self.value

class Input(UIElement):
	def __init__(self, x, y, w, h, text = "", font_size = 12, color = (50, 50, 50), text_color = (100, 100, 100)):
		super().__init__(x, y, w, h)
		self.text = text
		self.font_size = font_size
		self.font = pygame.font.SysFont("consolas", self.font_size)
		self.color = color
		self.text_color = text_color
		self.active = True
	def draw(self, surface, keyboard_just_pressed, mouse_buttons, mouse_position):
		if self.visible:
			self.update(keyboard_just_pressed, mouse_buttons, mouse_position)
			pygame.draw.rect(surface, self.color, self.rect)
			text = self.font.render(self.text, True, self.text_color)
			surface.blit(text, (self.position.x + 5, self.position.y + self.size.y / 2 - text.get_height() / 2))
	def update(self, keyboard_just_pressed, mouse_buttons, mouse_position):
		if self.active:
			for event in keyboard_just_pressed:
				if event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode




if __name__ == "__main__":
	print("This is a module for adding UI elements into pygame games/apps.")
	pygame.init()
	screen = pygame.display.set_mode((800, 600))
	clock = pygame.time.Clock()
	button = Button(100, 100, 100, 50)
	button.set_on_click(lambda: print("Hello, World!"))
	slider = Slider(100, 200, 100, 50, 0, 100)
	input = Input(100, 300, 100, 50)
	while True:
		screen.fill((0, 0, 0))
		mouse_just_pressed = [False, False, False]
		keyboard_just_pressed = []
		for event in pygame.event.get():
			if event.type == pygame.QUIT:   
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					quit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_just_pressed[event.button - 1] = True
			if event.type == pygame.MOUSEBUTTONUP:
				mouse_just_pressed[event.button - 1] = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					quit()
				else:
					keyboard_just_pressed.append(event)
		button.draw(screen, mouse_just_pressed, pygame.mouse.get_pos())
		slider.draw(screen, mouse_just_pressed, pygame.mouse.get_pos())
		input.draw(screen, keyboard_just_pressed, mouse_just_pressed, pygame.mouse.get_pos())
		print(input.text)

		pygame.display.update()
		clock.tick(60)