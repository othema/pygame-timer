import sys
import pygame


def exit_game():
    pygame.quit()
    sys.exit()


def calculate_center(window):
    return window.get_rect().center


def triangle(size, color):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()
    pygame.draw.polygon(surf, color, (rect.bottomleft, rect.midtop, rect.bottomright))
    return surf


def seconds_to_ms(seconds):
    minutes = seconds // 60
    seconds %= 60
    return minutes, seconds


def gradient(size, left, right):
    color_surf = pygame.Surface((2, 2))
    pygame.draw.line(color_surf, left, (0, 0), (0, 1))
    pygame.draw.line(color_surf, right, (1, 0), (1, 1))

    return pygame.transform.smoothscale(color_surf, size)


__all__ = ["exit_game", "calculate_center", "triangle", "seconds_to_ms", "gradient"]
