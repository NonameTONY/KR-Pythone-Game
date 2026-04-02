import json
from dataclasses import dataclass
from typing import List, Tuple

import pygame


TILE_SIZE = 32


@dataclass
class Tile:
    """Один тайл уровня: координаты и тип."""
    x: int
    y: int
    kind: str  # "solid" или "goal"


class GameLevel:
    """Класс уровня: загрузка, отрисовка и столкновения."""
    def __init__(self, json_path: str, solid_image: pygame.Surface, goal_image: pygame.Surface) -> None:
        self.json_path = json_path
        self.solid_image = solid_image
        self.goal_image = goal_image

        self.tiles: List[Tile] = []
        self.player_spawn: Tuple[int, int] = (64, 64)
        self.goal_rect: pygame.Rect | None = None

        self.load_or_create_default()

    def load_or_create_default(self) -> None:
        """Пытается загрузить уровень из JSON или создаёт простой уровень по умолчанию."""
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = self._create_default_data()
            self._save_data(data)

        self._from_data(data)

    def _create_default_data(self) -> dict:
        """Создаёт словарь с простой картой по умолчанию."""
        width = 30
        height = 15
        tiles: List[dict] = []

        # пол внизу
        for x in range(width):
            tiles.append({"x": x, "y": height - 2, "kind": "solid"})

        # несколько платформ
        for x in range(5, 10):
            tiles.append({"x": x, "y": 10, "kind": "solid"})
        for x in range(14, 20):
            tiles.append({"x": x, "y": 8, "kind": "solid"})

        # финиш
        tiles.append({"x": width - 3, "y": height - 3, "kind": "goal"})

        return {
            "tiles": tiles,
            "player_spawn": [64, 64],
        }

    def _save_data(self, data: dict) -> None:
        """Сохраняет данные уровня в JSON."""
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _from_data(self, data: dict) -> None:
        """Инициализирует уровень из словаря данных."""
        self.tiles.clear()
        for tile_dict in data.get("tiles", []):
            tile = Tile(
                x=int(tile_dict["x"]),
                y=int(tile_dict["y"]),
                kind=str(tile_dict.get("kind", "solid")),
            )
            self.tiles.append(tile)

        spawn = data.get("player_spawn", [64, 64])
        self.player_spawn = (int(spawn[0]), int(spawn[1]))

        # рассчитываем прямоугольник финиша
        self.goal_rect = None
        for tile in self.tiles:
            if tile.kind == "goal":
                rect = pygame.Rect(
                    tile.x * TILE_SIZE,
                    tile.y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                self.goal_rect = rect
                break

    def get_solid_rects(self) -> List[pygame.Rect]:
        """Возвращает список прямоугольников твёрдых тайлов для проверки столкновений."""
        rects: List[pygame.Rect] = []
        for tile in self.tiles:
            if tile.kind == "solid":
                rects.append(
                    pygame.Rect(
                        tile.x * TILE_SIZE,
                        tile.y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                    )
                )
        return rects

    def check_goal_reached(self, player_rect: pygame.Rect) -> bool:
        """Проверяет, достиг ли игрок финиша."""
        if self.goal_rect is None:
            return False
        return player_rect.colliderect(self.goal_rect)

    def render(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        """Отрисовывает все тайлы уровня с учётом смещения камеры."""
        offset_x, offset_y = offset
        for tile in self.tiles:
            world_x = tile.x * TILE_SIZE
            world_y = tile.y * TILE_SIZE
            screen_pos = (world_x - offset_x, world_y - offset_y)

            if tile.kind == "solid":
                surface.blit(self.solid_image, screen_pos)
            elif tile.kind == "goal":
                surface.blit(self.goal_image, screen_pos)