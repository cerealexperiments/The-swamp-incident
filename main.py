import pygame
import sys
from settings import *
from level import Level
from game_data import levels
from ui import UI


# IT WORKS LETSGOOOOOOOOOOOOOOOOOOO (last commit fr)
class Game:
    def __init__(self):
        # Player
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # Setup
        self.max_levels = len(levels)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.status = 'game'
        self.cur_level = 0
        self.display = pygame.Surface((self.screen_width, self.screen_height))
        self.font_name = "graphics/ui/8-BIT WONDER.TTF"
        self.WHITE = (255, 255, 255)
        self.death_sound = pygame.mixer.Sound("audio/effects/hit.wav")
        self.death_sound_replay = 0
        self.ending_music = pygame.mixer.Sound("audio/ending.wav")
        self.ending_music_replay = 0
        self.game_over = pygame.mixer.Sound("audio/game over.wav")
        self.game_over_replay = 0
        self.alive = True
        self.won = False

        # User interface
        self.ui = UI(screen)

    # Setup methods
    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.set_game, self.change_coins, self.change_health)
        self.status = 'level'

    def set_game(self):
        self.status = 'game'

    # Gameplay
    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount

    def check_game_over(self):
        if self.cur_health <= 0:
            if self.death_sound_replay < 1:
                self.death_sound.play()
                self.death_sound_replay += 1
            self.level.bg_music.stop()
            self.level.stomp_sound.set_volume(0)
            self.level.coin_sound.set_volume(0)
            screen.fill("black")
            self.draw_text("GAME OVER", 50, 650, 400)
            if self.game_over_replay < 1:
                self.game_over.play()
                self.game_over_replay += 1
            self.cur_health = 100
            self.coins = 0
            self.alive = False
            self.cur_level = self.cur_level
            self.set_game()
        # If player falls off
        elif self.level.player.sprite.rect.top > screen_height:
            if self.death_sound_replay < 1:
                self.death_sound.play()
                self.death_sound_replay += 1
            self.level.bg_music.stop()
            self.level.stomp_sound.set_volume(0)
            self.level.coin_sound.set_volume(0)
            screen.fill("black")
            self.draw_text("GAME OVER", 50, 650, 400)
            if self.game_over_replay < 1:
                self.game_over.play()
                self.game_over_replay += 1
            self.cur_health = 100
            self.coins = 0
            self.alive = False
            self.cur_level = self.cur_level
            self.set_game()

    def check_win(self):
        if pygame.sprite.spritecollide(self.level.player.sprite, self.level.goal, False):
            try:
                self.cur_level += 1
                self.level.bg_music.set_volume(0)
            except KeyError:
                self.alive = False
                self.won = True

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        screen.blit(text_surface, text_rect)

    def run(self):
        if self.status == 'game':
            try:
                self.create_level(self.cur_level)
                print(self.cur_level)
            except KeyError:
                self.alive = False
                self.won = True
        if self.alive:
            self.level.run()
            self.check_win()
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
        elif self.won:
            self.level.bg_music.set_volume(0)
            screen.fill("black")
            self.draw_text("THANKS FOR PLAYING", 50, 650, 400)
            if self.ending_music_replay < 1:
                self.ending_music.play()
                self.ending_music_replay += 1
        else:
            self.level.bg_music.set_volume(0)
            screen.fill("black")
            self.draw_text("GAME OVER", 50, 650, 400)


# Setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
background_image = pygame.image.load("graphics/decoration/Background.png")

# Cheat sound effects
invincibility = pygame.mixer.Sound("audio/invincibility.wav")
za_warudo = pygame.mixer.Sound("audio/za warudo.wav")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Toggle invincibility
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                game.max_health = 10000000000
                game.cur_health = 10000000000
                invincibility.play()
        # Use Za Warudo (doesn't work for now)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                game.level.enemy_speed = 0
                za_warudo.play()

    screen.fill("black")
    screen.blit(background_image, (0, 0))
    game.run()

    pygame.display.update()
    clock.tick(60)
