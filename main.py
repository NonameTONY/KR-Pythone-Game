import sys
import pygame

from level import GameLevel
from player import Player
from particles import ParticleSystem
from utils import load_image, load_sound


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FRAME_RATE = 60


class Game:
    """Главный класс игры: инициализация, игровой цикл и обработка событий."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Forest Runner")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # загрузка ресурсов
        self.background_image = load_image("background.png", fallback_color=(20, 20, 40))
        self.tile_image = load_image("tile_grass.png", fallback_color=(70, 200, 120))
        self.goal_image = load_image("tile_goal.png", fallback_color=(230, 210, 70))
        self.player_image = load_image("player.png", fallback_color=(240, 240, 255))

        self.jump_sound = load_sound("jump.wav")
        self.dash_sound = load_sound("dash.wav")
        self.music_started = False

        # игровые объекты
        self.level = GameLevel("level01.json", self.tile_image, self.goal_image)
        self.player = Player(self.level.player_spawn, self.player_image)
        self.particles = ParticleSystem()

        # параметры камеры
        self.camera_x = 0.0
        self.camera_y = 0.0

        self.running = True

    def handle_events(self) -> None:
        """Обрабатывает события Pygame (выход, нажатия клавиш)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                    if self.player.try_jump():
                        if self.jump_sound:
                            self.jump_sound.play()
                if event.key in (pygame.K_LSHIFT, pygame.K_x):
                    if self.player.try_start_dash():
                        if self.dash_sound:
                            self.dash_sound.play()

        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        self.player.set_horizontal_input(move_left, move_right)

    def update(self, delta_time: float) -> None:
        """Обновляет состояние мира: игрока, частицы, камеру."""
        self.player.update(self.level, delta_time, self.particles)
        self.particles.update(delta_time)

        # камера следует за игроком с плавным смещением
        target_x = self.player.rect.centerx - WINDOW_WIDTH // 2
        target_y = self.player.rect.centery - WINDOW_HEIGHT // 2
        smoothing = 0.12
        self.camera_x += (target_x - self.camera_x) * smoothing
        self.camera_y += (target_y - self.camera_y) * smoothing

        # запуск фоновой музыки (по возможности)
        if not self.music_started:
            try:
                pygame.mixer.music.load("music_background.ogg")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except pygame.error:
                # музыка не является критичной частью геймплея
                pass
            self.music_started = True

        # проверка достижения финиша
        if self.level.check_goal_reached(self.player.rect):
            print("Level finished!")
            # можно добавить переход на следующий уровень

    def render(self) -> None:
        """Рисует кадр: фон, уровень, игрока и частицы."""
        self.screen.fill((10, 10, 30))
        offset = (int(self.camera_x), int(self.camera_y))

        # фон со слабым параллаксом
        if self.background_image:
            bg_x = -offset[0] // 4
            bg_y = -offset[1] // 4
            self.screen.blit(self.background_image, (bg_x, bg_y))

        self.level.render(self.screen, offset)
        self.player.render(self.screen, offset)
        self.particles.render(self.screen, offset)

        pygame.display.flip()

    def run(self) -> None:
        """Запускает основной игровой цикл."""
        while self.running:
            delta_time = self.clock.tick(FRAME_RATE) / 1000.0
            self.handle_events()
            self.update(delta_time)
            self.render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()