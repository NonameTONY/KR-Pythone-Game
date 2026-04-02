import os
from typing import Optional, Tuple

import pygame


IMAGE_BASE_PATH = "data/images"
SOUND_BASE_PATH = "data/sfx"


def load_image(name: str, fallback_color: Tuple[int, int, int]) -> pygame.Surface:
    """Загружает изображение или создаёт простой цветной прямоугольник."""
    path = os.path.join(IMAGE_BASE_PATH, name)
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
    else:
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.fill(fallback_color)
    return image


def load_sound(name: str) -> Optional[pygame.mixer.Sound]:
    """Загружает звуковой файл, если он существует."""
    path = os.path.join(SOUND_BASE_PATH, name)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None