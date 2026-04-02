from typing import List, Tuple

import pygame


class Particle:
    """Одна частица с позицией, скоростью и временем жизни."""

    def __init__(self, position: Tuple[int, int]) -> None:
        self.x, self.y = position
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.life_time = 0.25

    def update(self, delta_time: float) -> None:
        """Обновляет состояние частицы."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.life_time -= delta_time

    def is_alive(self) -> bool:
        """Возвращает True, если частица ещё жива."""
        return self.life_time > 0.0


class ParticleSystem:
    """Управляет созданием и отрисовкой частиц."""

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def spawn_trail(self, position: Tuple[int, int]) -> None:
        """Создаёт небольшой след частиц в указанной позиции."""
        for _ in range(6):
            particle = Particle(position)
            particle.velocity_x = -80.0
            particle.velocity_y = 40.0
            self.particles.append(particle)

    def update(self, delta_time: float) -> None:
        """Обновляет список частиц, удаляя отжившие."""
        for particle in self.particles[:]:
            particle.update(delta_time)
            if not particle.is_alive():
                self.particles.remove(particle)

    def render(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        """Рисует частицы маленькими полупрозрачными кругами."""
        offset_x, offset_y = offset
        for particle in self.particles:
            alpha = max(0, min(255, int(particle.life_time * 255)))
            color = (255, 255, 255, alpha)
            temp_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (4, 4), 4)
            surface.blit(temp_surface, (particle.x - offset_x - 4, particle.y - offset_y - 4))