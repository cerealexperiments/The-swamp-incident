import pygame 
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Box, Coin
from enemy import Enemy
from decoration import Water
from player import Player
from particles import ParticleEffect
from game_data import levels


class Level:
	def __init__(self, current_level, surface, create_game, change_coins, change_health):
		# General setup
		self.display_surface = surface
		self.world_shift = 0
		self.current_x = None

		self.create_game = create_game
		self.current_level = current_level
		level_data = levels[self.current_level]

		# Sounds
		self.bg_music = pygame.mixer.Sound("audio/background.wav")
		self.coin_sound = pygame.mixer.Sound("audio/effects/coin.wav")
		self.coin_sound.set_volume(0.3)
		self.stomp_sound = pygame.mixer.Sound("audio/effects/stomp.wav")
		self.stomp_sound.set_volume(0.6)

		# Background music
		self.bg_music.play()
		self.bg_music.set_volume(0.1)

		# Player setup
		player_layout = import_csv_layout(level_data["player"])
		self.player = pygame.sprite.GroupSingle()
		self.goal = pygame.sprite.GroupSingle()
		self.player_setup(player_layout, change_health)
		self.dust_sprite = pygame.sprite.GroupSingle()
		self.player_on_ground = False

		# User Interface
		self.change_coins = change_coins

		# Terrain setup
		terrain_layout = import_csv_layout(level_data["terrain"])
		self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

		# Boxes
		box_layout = import_csv_layout(level_data["boxes"])
		self.boxes_sprites = self.create_tile_group(box_layout, "boxes")

		# Grass setup
		grass_layout = import_csv_layout(level_data["grass"])
		self.grass_sprites = self.create_tile_group(grass_layout, "grass")

		# Coins
		coin_layout = import_csv_layout(level_data["coins"])
		self.coin_sprites = self.create_tile_group(coin_layout, "coins")

		# Enemy
		enemy_layout = import_csv_layout(level_data["enemies"])
		self.enemy_sprites = self.create_tile_group(enemy_layout, "enemies")

		# Enemy death effect
		self.enemy_death_sprites = pygame.sprite.Group()

		# Constraints
		constraint_layout = import_csv_layout(level_data["constraints"])
		self.constraint_sprites = self.create_tile_group(constraint_layout, "constraint")

		# Decorations
		level_width = len(terrain_layout[0]) * tile_size
		self.water = Water(screen_height - 20, level_width)

	@staticmethod
	def create_tile_group(layout, type):
		sprite_group = pygame.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != "-1":
					x = col_index * tile_size
					y = row_index * tile_size
					if type == "terrain":
						terrain_tile_list = import_cut_graphics("graphics/terrain/terrain_tiles.png")
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size, x, y, tile_surface)
					if type == "grass":
						grass_tile_list = import_cut_graphics("graphics/decoration/grass/grass.png")
						tile_surface = grass_tile_list[int(val)]
						sprite = StaticTile(tile_size, x, y, tile_surface)
					if type == "boxes":
						sprite = Box(tile_size, x, y)
					if type == "coins":
						if val == "0":
							sprite = Coin(tile_size, x, y, "graphics/coins/gold", 5)
						elif val == "1":
							sprite = Coin(tile_size, x, y, "graphics/coins/silver", 1)
					if type == "enemies":
						sprite = Enemy(tile_size, x, y)
					if type == "constraint":
						sprite = Tile(tile_size, x, y)
					sprite_group.add(sprite)
		return sprite_group

	def player_setup(self, layout, change_health):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * tile_size
				y = row_index * tile_size
				if val == "0":
					sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health)
					self.player.add(sprite)
				if val == "1":
					pointer_surface = pygame.image.load("graphics/character/pointer.png").convert_alpha()
					sprite = StaticTile(tile_size, x, y, pointer_surface)
					self.goal.add(sprite)

	def create_jump_particles(self, pos):
		if self.player.sprite.facing_right:
			pos -= pygame.math.Vector2(10, 5)
		else:
			pos += pygame.math.Vector2(10, -5)
		jump_particle_sprite = ParticleEffect(pos, "jump")
		self.dust_sprite.add(jump_particle_sprite)

	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
				enemy.reverse()

	# Player movements
	def horizontal_movement_collision(self):
		player = self.player.sprite
		player.collision_rect.x += player.direction.x * player.speed
		collidable_sprites = self.terrain_sprites.sprites() + self.boxes_sprites.sprites()
		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if player.direction.x < 0:
					player.collision_rect.left = sprite.rect.right
					player.on_left = True
					self.current_x = player.collision_rect.left
				elif player.direction.x > 0:
					player.collision_rect.right = sprite.rect.left
					player.on_right = True

	def scroll_x(self):
		player = self.player.sprite
		player_x = player.collision_rect.centerx
		direction_x = player.direction.x

		if player_x < screen_width / 2 and direction_x < 0:
			self.world_shift = 8
			player.speed = 0
		elif player_x > screen_width - (screen_width / 2) and direction_x > 0:
			self.world_shift = -8
			player.speed = 0
		else:
			self.world_shift = 0
			player.speed = 8

	def vertical_movement_collision(self):
		player = self.player.sprite
		player.apply_gravity()
		collidable_sprites = self.terrain_sprites.sprites() + self.boxes_sprites.sprites()
		for sprite in collidable_sprites:
			if sprite.rect.colliderect(player.collision_rect):
				if player.direction.y > 0:
					player.collision_rect.bottom = sprite.rect.top
					player.direction.y = 0
					player.on_ground = True
				elif player.direction.y < 0:
					player.collision_rect.top = sprite.rect.bottom
					player.direction.y = 0
					player.on_ceiling = True

		if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
			player.on_ground = False

	def get_player_on_ground(self):
		if self.player.sprite.on_ground:
			self.player_on_ground = True
		else:
			self.player_on_ground = False

	def create_landing_dust(self):
		if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
			if self.player.sprite.facing_right:
				offset = pygame.math.Vector2(10, 15)
			else:
				offset = pygame.math.Vector2(-10, 15)
			fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
			self.dust_sprite.add(fall_dust_particle)

	def check_win(self):
		if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
			print('Wong')
			self.create_game()

	# Coin collisions
	def check_coin_collisions(self):
		collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
		if collided_coins:
			self.coin_sound.play()
			for coin in collided_coins:
				self.change_coins(coin.value)

	# Enemy collisions
	def check_enemy_collisions(self):
		enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
		if enemy_collisions:
			for enemy in enemy_collisions:
				enemy_center = enemy.rect.centery
				enemy_top = enemy.rect.top
				player_bottom = self.player.sprite.rect.bottom
				if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
					self.stomp_sound.play()
					self.player.sprite.direction.y = -16
					enemy_death_effect = ParticleEffect((enemy.rect.x+20, enemy.rect.y + 35), "enemy_death")
					self.enemy_death_sprites.add(enemy_death_effect)
					enemy.kill()
				else:
					self.player.sprite.get_damage()

	# Runs the level
	def run(self):
		# Dust particles
		self.dust_sprite.update(self.world_shift)
		self.dust_sprite.draw(self.display_surface)

		# Terrain
		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)

		# Enemy
		self.enemy_sprites.update(self.world_shift)
		self.constraint_sprites.update(self.world_shift)
		self.enemy_collision_reverse()
		self.enemy_sprites.draw(self.display_surface)
		self.enemy_death_sprites.update(self.world_shift)
		self.enemy_death_sprites.draw(self.display_surface)

		# Grass
		self.grass_sprites.update(self.world_shift)
		self.grass_sprites.draw(self.display_surface)

		# Box
		self.boxes_sprites.update(self.world_shift)
		self.boxes_sprites.draw(self.display_surface)

		# Coins
		self.coin_sprites.update(self.world_shift)
		self.coin_sprites.draw(self.display_surface)

		# Player sprites
		self.player.update()
		self.horizontal_movement_collision()
		self.get_player_on_ground()
		self.vertical_movement_collision()
		self.create_landing_dust()
		self.scroll_x()
		self.player.draw(self.display_surface)
		self.goal.update(self.world_shift)
		self.goal.draw(self.display_surface)
		self.check_enemy_collisions()
		self.check_coin_collisions()

		self.check_win()

		# Water
		self.water.draw(self.display_surface, self.world_shift)
