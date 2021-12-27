import pygame
from support import import_folder


class ParticleEffect(pygame.sprite.Sprite):
	def __init__(self, pos, type):
		super().__init__()
		self.frame_index = 0
		self.animation_speed = 0.5
		self.type = None
		if type == 'jump':
			self.type = "jump"
			self.frames = import_folder('graphics/character/dust_particles/jump')
		if type == 'land':
			self.type = "land"
			self.frames = import_folder('graphics/character/dust_particles/land')
		if type == "enemy_death":
			self.type = "enemy_death"
			self.animation_speed = 0.15
			self.frames = import_folder("graphics/enemy/take hit")
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(center=pos)

	def animate(self):
		self.frame_index += self.animation_speed
		if self.frame_index >= len(self.frames):
			self.kill()
		else:
			self.image = self.frames[int(self.frame_index)]

	def reverse_image(self):
		self.image = pygame.transform.flip(self.image, True, False)

	def update(self, x_shift):
		self.animate()
		self.rect.x += x_shift
