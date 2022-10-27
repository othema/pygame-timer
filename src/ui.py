import pygame

font_cache = {}
cached_hover = {}
was_mouse_down = False


class TextData:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.w, self.h = x, y, width, height


def cache_name(name, size, bold=False, italic=False):
    return str(name) + str(size) + str(bold) + str(italic)


def cache(font, name):
    font_cache[name] = font
    return font


def get_font(name, size, bold=False, italic=False) -> pygame.font.Font:
    cname = cache_name(name, size, bold, italic)
    try:
        return font_cache[cname]
    except KeyError:
        try:
            return cache(pygame.font.Font(name, size), cname)
        except FileNotFoundError:
            return cache(pygame.font.SysFont(name, size, bold=bold, italic=italic), cname)


def text(dest, txt, position, size=32, color=(255, 255, 255), font=None, aa=True, align="top-left", bold=False,
         italic=False):
    surf = get_font(font, size, bold, italic).render(txt, aa, color)
    pos = align_font(position, align, surf)
    dest.blit(surf, pos)
    return pygame.Rect(*pos, *surf.get_size())


def text_data(txt, position, size=32, font=None, align="top-left", bold=False, italic=False) -> TextData:
    surf = get_font(font, size, bold, italic).render(txt, False, (0, 0, 0))
    pos = align_font(position, align, surf)
    data = TextData(*pos, surf.get_width(), surf.get_height())
    return data


def button(dest, txt, position, size=32, text_color=(0, 0, 0), bg_color=(255, 255, 255), bg_color_hover=(230, 230, 230),
           font=None, aa=True, align="top-left", padding=5, border_radius=0, bold=False, italic=False, width=None,
           hover_sound=None, disabled=False):
    global was_mouse_down

    data = text_data(txt, position, size, font, align, bold, italic)

    mod = 0
    if width is not None:
        mod = (width - data.w) / 2

    rect = pygame.Rect(data.x - padding - mod, data.y - padding, data.w + padding * 2 + mod * 2, data.h + padding * 2)

    hover = not disabled and rect.collidepoint(*pygame.mouse.get_pos())
    color = darken_color(bg_color, 80) if disabled else (bg_color_hover if hover else bg_color)

    pygame.draw.rect(dest, color, rect, border_radius=border_radius)
    text(dest, txt, position, size, text_color, font, aa, align, bold, italic)

    cname = cache_name(txt + str(position), size, bold, italic)
    try:
        if cached_hover[cname] and not hover:  # Just ended hovering
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif not cached_hover[cname] and hover:  # Just started hovering
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if hover_sound is not None: hover_sound.play()
    except KeyError:
        pass
    cached_hover[cname] = hover

    clicked = False
    if hover:
        mouse_down = pygame.mouse.get_pressed(3)[0]
        clicked = hover and (was_mouse_down and not mouse_down)

        if clicked:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Stops a bug when button stops being rendered

        was_mouse_down = mouse_down
    return clicked


def align_font(position, align, surf) -> list:
    pos = list(position)
    split = align.split("-")

    if split[0] == "bottom":
        pos[1] -= surf.get_height()
    elif split[0] == "center":
        pos[1] -= surf.get_height() / 2

    if split[1] == "right":
        pos[0] -= surf.get_width()
    elif split[1] == "center":
        pos[0] -= surf.get_width() / 2

    return pos


def darken_color(color, amount):
    new = []
    for value in color:
        new.append(min(255, max(0, value - amount)))
    return tuple(new)


__all__ = ["text", "button", "darken_color"]
