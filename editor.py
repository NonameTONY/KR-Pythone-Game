import json
from typing import List, Tuple

import pygame

from level import TILE_SIZE


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FRAME_RATE = 60
JSON_PATH = "level01.json"

COLOR_GRID = (60, 60, 60)
COLOR_BACKGROUND = (15, 15, 15)
COLOR_SOLID = (90, 200, 140)
COLOR_GOAL = (230, 210, 70)


class LevelEditor:
    """Простой редактор уровней с сохранением в JSON."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Level editor")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.camera_x = 0
        self.camera_y = 0
        self.running = True
        self.show_grid = True

        self.tiles: List[Tuple[int, int, str]] = []
        self.player_spawn = (64, 64)
        self.current_kind = "solid"  # solid / goal

        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Загружает существующую карту из JSON, если файл есть."""
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return

        self.tiles.clear()
        for tile in data.get("tiles", []):
            self.tiles.append((int(tile["x"]), int(tile["y"]), str(tile.get("kind", "solid"))))

        spawn = data.get("player_spawn", [64, 64])
        self.player_spawn = (int(spawn[0]), int(spawn[1]))

    def _save(self) -> None:
        """Сохраняет текущую карту в JSON."""
        tiles_data = []
        for x, y, kind in self.tiles:
            tiles_data.append({"x": x, "y": y, "kind": kind})

        data = {
            "tiles": tiles_data,
            "player_spawn": list(self.player_spawn),
        }

        with open(JSON_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Level saved to {JSON_PATH}")

    def _toggle_kind(self) -> None:
        """Переключает тип редактируемого блока."""
        if self.current_kind == "solid":
            self.current_kind = "goal"
        else:
            self.current_kind = "solid"

    def _set_tile(self, grid_x: int, grid_y: int, kind: str) -> None:
        """Устанавливает тайл указанного типа в клетку сетки."""
        for index, (tx, ty, _) in enumerate(self.tiles):
            if tx == grid_x and ty == grid_y:
                self.tiles[index] = (grid_x, grid_y, kind)
                return
        self.tiles.append((grid_x, grid_y, kind))

    def _remove_tile(self, grid_x: int, grid_y: int) -> None:
        """Удаляет тайл из клетки сетки, если он там есть."""
        self.tiles = [(x, y, k) for (x, y, k) in self.tiles if not (x == grid_x and y == grid_y)]

    def handle_events(self) -> None:
        """Обрабатывает события Pygame: мышь, клавиатура."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_s:
                    self._save()
                if event.key == pygame.K_l:
                    self._load_if_exists()
                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                if event.key == pygame.K_TAB:
                    self._toggle_kind()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x + self.camera_x
                world_y = mouse_y + self.camera_y
                grid_x = world_x // TILE_SIZE
                grid_y = world_y // TILE_SIZE

                if event.button == 1:
                    self._set_tile(grid_x, grid_y, self.current_kind)
                if event.button == 3:
                    self._remove_tile(grid_x, grid_y)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.camera_x -= 10
        if keys[pygame.K_d]:
            self.camera_x += 10
        if keys[pygame.K_w]:
            self.camera_y -= 10
        if keys[pygame.K_s]:
            self.camera_y += 10

    def draw(self) -> None:
        """Рисует текущую карту и сетку редактора."""
        self.screen.fill(COLOR_BACKGROUND)

        # тайлы
        for x, y, kind in self.tiles:
            screen_x = x * TILE_SIZE - self.camera_x
            screen_y = y * TILE_SIZE - self.camera_y
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            color = COLOR_SOLID if kind == "solid" else COLOR_GOAL
            pygame.draw.rect(self.screen, color, rect)

        # выделение текущего типа блока
        pygame.draw.rect(self.screen, COLOR_SOLID if self.current_kind == "solid" else COLOR_GOAL,
                         pygame.Rect(10, 10, 24, 24))

        # сетка
        if self.show_grid:
            for x in range(0, WINDOW_WIDTH, TILE_SIZE):
                pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
            for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
                pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

        pygame.display.flip()

    def run(self) -> None:
        """Запускает основной цикл редактора."""
        while self.running:
            self.clock.tick(FRAME_RATE)
            self.handle_events()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    LevelEditor().run()