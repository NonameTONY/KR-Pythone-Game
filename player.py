from typing import Tuple

import pygame

from level import GameLevel, TILE_SIZE
from particles import ParticleSystem


GRAVITY = 2000.0
MOVE_SPEED = 260.0
JUMP_SPEED = 680.0
DASH_SPEED = 900.0
DASH_TIME = 0.14


class Player:
    """Игровой персонаж с простой физикой и рывком."""

    def __init__(self, spawn_position: Tuple[int, int], image: pygame.Surface) -> None:
        self.image = image
        self.rect = self.image.get_rect(topleft=spawn_position)

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.on_ground = False
        self.want_move_left = False
        self.want_move_right = False

        self.dashing = False
        self.dash_time_left = 0.0
        self.dash_direction = 0

    def set_horizontal_input(self, left_pressed: bool, right_pressed: bool) -> None:
        """Запоминает горизонтальный ввод игрока."""
        self.want_move_left = left_pressed
        self.want_move_right = right_pressed

    def try_jump(self) -> bool:
        """Пытается выполнить прыжок, если персонаж стоит на земле."""
        if self.on_ground and not self.dashing:
            self.velocity_y = -JUMP_SPEED
            self.on_ground = False
            return True
        return False

    def try_start_dash(self) -> bool:
        """Пытается запустить рывок, если сейчас рывка нет."""
        if self.dashing:
            return False

        direction = 0
        if self.want_move_left:
            direction = -1
        elif self.want_move_right:
            direction = 1

        if direction == 0:
            return False

        self.dashing = True
        self.dash_direction = direction
        self.dash_time_left = DASH_TIME
        return True

    def _apply_horizontal_input(self, delta_time: float) -> None:
        """Обновляет горизонтальную скорость персонажа."""
        if self.dashing:
            self.velocity_x = self.dash_direction * DASH_SPEED
            return

        target_speed = 0.0
        if self.want_move_left:
            target_speed -= MOVE_SPEED
        if self.want_move_right:
            target_speed += MOVE_SPEED

        acceleration = 2200.0
        if target_speed > self.velocity_x:
            self.velocity_x = min(target_speed, self.velocity_x + acceleration * delta_time)
        elif target_speed < self.velocity_x:
            self.velocity_x = max(target_speed, self.velocity_x - acceleration * delta_time)

    def _move_and_collide(self, level: GameLevel, delta_x: float, delta_y: float) -> None:
        """Перемещает персонажа и обрабатывает столкновения по каждой оси отдельно."""
        if delta_x != 0.0:
            self.rect.x += int(delta_x)
            for tile_rect in level.get_solid_rects():
                if self.rect.colliderect(tile_rect):
                    if delta_x > 0:
                        self.rect.right = tile_rect.left
                    else:
                        self.rect.left = tile_rect.right
                    self.velocity_x = 0.0

        if delta_y != 0.0:
            self.rect.y += int(delta_y)
            for tile_rect in level.get_solid_rects():
                if self.rect.colliderect(tile_rect):
                    if delta_y > 0:
                        self.rect.bottom = tile_rect.top
                        self.on_ground = True
                    else:
                        self.rect.top = tile_rect.bottom
                    self.velocity_y = 0.0

    def update(self, level: GameLevel, delta_time: float, particles: ParticleSystem) -> None:
        """Обновляет состояние персонажа."""
        if self.dashing:
            self.dash_time_left -= delta_time
            if self.dash_time_left <= 0:
                self.dashing = False

        self._apply_horizontal_input(delta_time)

        if not self.on_ground:
            self.velocity_y += GRAVITY * delta_time
        else:
            self.velocity_y = min(self.velocity_y, 0.0)

        move_x = self.velocity_x * delta_time
        move_y = self.velocity_y * delta_time

        self.on_ground = False
        self._move_and_collide(level, move_x, 0.0)
        self._move_and_collide(level, 0.0, move_y)

        if self.dashing:
            particles.spawn_trail(self.rect.center)

        # ограничиваем падение вниз, чтобы игрок не «улетал» слишком далеко
        max_y = level.player_spawn[1] + 30 * TILE_SIZE
        if self.rect.y > max_y:
            self.rect.topleft = level.player_spawn
            self.velocity_x = 0.0
            self.velocity_y = 0.0

    def render(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        """Рисует персонажа на экране с учётом смещения камеры."""
        offset_x, offset_y = offset
        surface.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))