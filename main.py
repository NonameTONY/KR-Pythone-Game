import sys
import subprocess
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

        # шрифты для интерфейса и окна завершения уровня
        self.font_large = pygame.font.SysFont(None, 64)
        self.font_small = pygame.font.SysFont(None, 32)

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

        # состояние игры
        self.game_state = "running"  # running / completed
        self.running = True

        # кнопки окна завершения уровня
        self.restart_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 160,
            WINDOW_HEIGHT // 2 + 40,
            140,
            50,
        )
        self.edit_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 + 20,
            WINDOW_HEIGHT // 2 + 40,
            180,
            50,
        )

    def handle_events(self) -> None:
        """Обрабатывает события Pygame: выход, управление, клики по кнопкам."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state == "running":
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

            elif self.game_state == "completed":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_r:
                        self.restart_level()
                    if event.key == pygame.K_e:
                        self.open_editor_and_reload()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.restart_button_rect.collidepoint(event.pos):
                        self.restart_level()
                    elif self.edit_button_rect.collidepoint(event.pos):
                        self.open_editor_and_reload()

        if self.game_state == "running":
            keys = pygame.key.get_pressed()
            move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            self.player.set_horizontal_input(move_left, move_right)
        else:
            self.player.set_horizontal_input(False, False)

    def update(self, delta_time: float) -> None:
        """Обновляет состояние мира: игрока, частицы, камеру."""
        if self.game_state != "running":
            return

        self.player.update(self.level, delta_time, self.particles)
        self.particles.update(delta_time)

        # камера следует за игроком с плавным смещением
        target_x = self.player.rect.centerx - WINDOW_WIDTH // 2
        target_y = self.player.rect.centery - WINDOW_HEIGHT // 2
        smoothing = 0.12
        self.camera_x += (target_x - self.camera_x) * smoothing
        self.camera_y += (target_y - self.camera_y) * smoothing

        # запуск фоновой музыки
        if not self.music_started:
            try:
                pygame.mixer.music.load("music_background.ogg")
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass
            self.music_started = True

        # проверка достижения финиша
        if self.level.check_goal_reached(self.player.rect):
            self.game_state = "completed"

    def restart_level(self) -> None:
        """Перезапускает текущий уровень."""
        self.level = GameLevel("level01.json", self.tile_image, self.goal_image)
        self.player = Player(self.level.player_spawn, self.player_image)
        self.particles = ParticleSystem()
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.game_state = "running"

    def open_editor_and_reload(self) -> None:
        """Открывает редактор уровней и после его закрытия перезагружает карту."""
        try:
            subprocess.run([sys.executable, "editor.py"], check=False)
        except Exception as error:
            print(f"Не удалось запустить editor.py: {error}")

        self.restart_level()

    def render_level_completed_overlay(self) -> None:
        """Рисует окно завершения уровня с двумя кнопками."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 250,
            WINDOW_HEIGHT // 2 - 110,
            500,
            220,
        )

        pygame.draw.rect(self.screen, (30, 30, 60), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (220, 220, 240), panel_rect, 2, border_radius=12)

        title_surface = self.font_large.render("Level passed!", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(title_surface, title_rect)

        hint_surface = self.font_small.render("Choose what to do next", True, (210, 210, 230))
        hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 5))
        self.screen.blit(hint_surface, hint_rect)

        mouse_position = pygame.mouse.get_pos()

        restart_color = (90, 190, 120)
        if self.restart_button_rect.collidepoint(mouse_position):
            restart_color = (120, 220, 150)

        edit_color = (210, 180, 80)
        if self.edit_button_rect.collidepoint(mouse_position):
            edit_color = (235, 205, 100)

        pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, edit_color, self.edit_button_rect, border_radius=8)

        restart_text = self.font_small.render("Restart", True, (20, 20, 20))
        restart_text_rect = restart_text.get_rect(center=self.restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        edit_text = self.font_small.render("Edit level", True, (20, 20, 20))
        edit_text_rect = edit_text.get_rect(center=self.edit_button_rect.center)
        self.screen.blit(edit_text, edit_text_rect)

        hotkeys_text = self.font_small.render("R - restart, E - edit level", True, (180, 180, 210))
        hotkeys_rect = hotkeys_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 95))
        self.screen.blit(hotkeys_text, hotkeys_rect)

    def render(self) -> None:
        """Рисует кадр: фон, уровень, игрока и частицы."""
        self.screen.fill((10, 10, 30))
        offset = (int(self.camera_x), int(self.camera_y))

        if self.background_image:
            bg_x = -offset[0] // 4
            bg_y = -offset[1] // 4
            self.screen.blit(self.background_image, (bg_x, bg_y))

        self.level.render(self.screen, offset)
        self.player.render(self.screen, offset)
        self.particles.render(self.screen, offset)

        if self.game_state == "completed":
            self.render_level_completed_overlay()

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