import pygame
import time
from enum import Enum

from src.constants import *
from src.ui import text, text_data, darken_color
from src.helpers import *


def main():
    def render():
        nonlocal progress_lerp

        if timer_running:
            percent_finished = round(time_elapsed / timer_total * window.get_height())
            target = window.get_height() - percent_finished
            progress_lerp += (target - progress_lerp) / 10
            pygame.draw.rect(window, darken_color(WINDOW_COLOR, 5), (0, 0, window.get_width(), progress_lerp))

        window_multiplier = window.get_width() / 600

        font_size = int(window_multiplier * 140)

        m, s = seconds_to_ms(timer_total - time_elapsed)
        mins = str(m if timer_running else minutes).zfill(2)
        secs = str(s if timer_running else seconds).zfill(2)
        data_whole = text_data(f"{mins}:{secs}", center, font_size, TIMER_FONT, "center-center")

        if timer_running:
            left_color = TIMER_COLOR_ACTIVE
            right_color = TIMER_COLOR_ACTIVE
            colon_color = TIMER_COLOR_ACTIVE
        else:
            colon_color = TIMER_COLOR_INACTIVE
            if timer_side == TimerSide.LEFT:
                left_color = TIMER_COLOR_ACTIVE
                right_color = TIMER_COLOR_INACTIVE
            else:
                left_color = TIMER_COLOR_INACTIVE
                right_color = TIMER_COLOR_ACTIVE

        mins_rect = text(window, mins, (data_whole.x, data_whole.y), font_size, left_color, font=TIMER_FONT)
        colon_rect = text(window, ":", (mins_rect.x + mins_rect.w, data_whole.y), font_size, colon_color, font=TIMER_FONT)
        text(window, secs, (colon_rect.x + colon_rect.w, data_whole.y), font_size, right_color, font=TIMER_FONT)

        kbd_y = min(window.get_height() - 50, colon_rect.bottom + 100)
        draw_kbd_ui(kbd_y, window_multiplier)

    def draw_kbd_ui(y, window_multiplier):
        spacing = min(300, int(window_multiplier * 150))

        window.blit(surf_kbd_arrows, (center[0] - surf_kbd_arrows.get_width() / 2 - spacing, y - surf_kbd_arrows.get_height()))
        window.blit(surf_kbd_space, (center[0] - surf_kbd_space.get_width() / 2, y - surf_kbd_space.get_height()))
        window.blit(surf_kbd_r, (center[0] - surf_kbd_r.get_width() / 2 + spacing, y - surf_kbd_r.get_height()))

        text(window, "TO SET TIMER", (center[0] - spacing, y+7), 14, (100, 100, 100), UI_FONT, align="top-center")
        t = "TO START/STOP" if not timer_running else ("TO START" if timer_paused else "TO STOP")
        text(window, t, (center[0], y+7), 14, (100, 100, 100), UI_FONT, align="top-center")
        text(window, "TO RESET", (center[0] + spacing, y+7), 14, (100, 100, 100), UI_FONT, align="top-center")

    def increment_active_side(amount):
        nonlocal seconds, minutes
        if timer_side == TimerSide.LEFT:
            minutes += amount
            if minutes < 0:
                minutes = 0
        else:
            seconds += amount
            if seconds < 0:
                seconds = 0

    def set_timer_state(running, paused=False):
        nonlocal timer_running, timer_paused, time_elapsed

        if not running:
            timer_paused = False
            timer_running = False
            pygame.time.set_timer(CLOCK_TICK, 0)
            time_elapsed = 0
            return

        timer_running = True
        if paused:
            timer_paused = True
            pygame.time.set_timer(CLOCK_TICK, 0)
        else:
            timer_paused = False
            pygame.time.set_timer(CLOCK_TICK, 1000)

    # Initialise pygame
    pygame.init()

    # Create window
    flags = pygame.RESIZABLE if WINDOW_RESIZABLE else None
    window = pygame.display.set_mode(WINDOW_SIZE, flags=flags)
    pygame.display.set_caption(WINDOW_TITLE)
    center = calculate_center(window)

    pygame.key.set_repeat(450, 65)
    clock = pygame.time.Clock()

    # App variables
    timer_side = TimerSide.LEFT
    minutes = 10
    seconds = 0
    progress_lerp = 0

    # Timer variables
    timer_running = False
    timer_paused = False
    time_elapsed = 0
    timer_total = 0

    # Surfaces
    surf_kbd_arrows = pygame.transform.scale(pygame.image.load("img/kbd_arrows.png"), (146, 66)).convert_alpha()
    surf_kbd_space = pygame.transform.scale(pygame.image.load("img/kbd_space.png"), (144, 33)).convert_alpha()
    surf_kbd_r = pygame.transform.scale(pygame.image.load("img/kbd_r.png"), (60, 33)).convert_alpha()
    background = get_background(window.get_size())

    # Sounds
    alarm_channel = pygame.mixer.Channel(1)
    alarm_sound = pygame.mixer.Sound(ALARM_SOUND)

    CLOCK_TICK = pygame.USEREVENT
    set_timer_state(False)

    while True:
        clock.tick(FPS)

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()

            # On resize, update window center variable
            if event.type == pygame.VIDEORESIZE:
                center = calculate_center(window)
                background = get_background(window.get_size())

            if event.type == CLOCK_TICK:
                time_elapsed += 1
                if time_elapsed > timer_total:
                    # Timer finished
                    set_timer_state(False, False)
                    alarm_channel.play(alarm_sound, -1)

            if event.type == pygame.KEYDOWN:
                if alarm_channel.get_busy():
                    alarm_sound.stop()

                if event.key == pygame.K_LEFT:
                    timer_side = TimerSide.LEFT
                elif event.key == pygame.K_RIGHT:
                    timer_side = TimerSide.RIGHT
                elif event.key == pygame.K_SPACE:
                    if timer_running:  # Toggle pause
                        set_timer_state(True, not timer_paused)
                    else:
                        # Timer just stared
                        timer_total = minutes * 60 + seconds
                        set_timer_state(True, False)

                elif event.key == pygame.K_r:
                    set_timer_state(False, False)

                if not timer_running:
                    if event.key == pygame.K_UP:
                        increment_active_side(1)
                    if event.key == pygame.K_DOWN:
                        increment_active_side(-1)

        # Render app
        window.blit(background, (0, 0))
        render()
        pygame.display.update()


def get_background(size, color=WINDOW_COLOR):
    new_size = size[1], size[0]
    return pygame.transform.rotate(gradient(new_size, darken_color(color, -10), color).convert(), -90)


class AppScreen(Enum):
    HOME = 1


class TimerSide(Enum):
    LEFT = 1
    RIGHT = 2


main()
