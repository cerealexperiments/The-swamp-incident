import pygame
import sys
from settings import *
from level import Level
from game_data import levels
from ui import UI


# IT WORKS LETSGOOOOOOOOOOOOOOOOOOO
class Game:
    def __init__(self):
        self.max_levels = len(levels)
        # Player
        self.max_health = 100
        self.cur_health = 100
        self.coins = 0

        # Setup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.status = 'game'
        self.cur_level = 0
        self.display = pygame.Surface((self.screen_width, self.screen_height))
        self.font_name = "graphics/ui/8-BIT WONDER.TTF"
        self.WHITE = (255, 255, 255)
        self.death_sound = pygame.mixer.Sound("audio/effects/hit.wav")
        self.death_sound_replay = 0
        self.alive = True
        self.won = False

        # User interface
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.set_game, self.change_coins, self.change_health)
        self.status = 'level'

    def set_game(self):
        self.status = 'game'

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.cur_health += amount

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.alive = True

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
            self.cur_health = 100
            self.coins = 0
            self.alive = False
            self.cur_level = self.cur_level
            self.set_game()

        elif self.level.player.sprite.rect.top > screen_height:
            if self.death_sound_replay < 1:
                self.death_sound.play()
                self.death_sound_replay += 1
            self.level.bg_music.stop()
            self.level.stomp_sound.set_volume(0)
            self.level.coin_sound.set_volume(0)
            screen.fill("black")
            self.draw_text("GAME OVER", 50, 650, 400)
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
            pygame.mixer.pause()
            screen.fill("black")
            self.draw_text("THANKS FOR PLAYING", 50, 650, 400)
        else:
            self.level.bg_music.set_volume(0)
            pygame.mixer.pause()
            screen.fill("black")
            self.draw_text("GAME OVER", 50, 650, 400)


# setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()
background_image = pygame.image.load("graphics/decoration/Background.png")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill("black")
    screen.blit(background_image, (0, 0))
    game.run()

    pygame.display.update()
    clock.tick(60)
