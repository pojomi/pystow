import curses as c
from curses import window, init_pair, init_color, color_pair as color, use_default_colors
from classes import WinProps
from hex_to_rgb import hex_to_rgb

def stdscr_setup() -> None:
    is_color_tty:bool = c.has_colors()
    changeable_color:bool = c.can_change_color()

    if is_color_tty:
        if changeable_color:
            # Full color palette
            init_color(0, *hex_to_rgb('#2c343a'))
            init_color(1, *hex_to_rgb('#e67c7f'))
            # init_color(2, *hex_to_rgb('#a9c181'))
            # init_color(3, *hex_to_rgb('#ddbd7f'))
            init_color(4, *hex_to_rgb('#7fbcb4'))
            # init_color(5, *hex_to_rgb('#d69ab7'))
            init_color(6, *hex_to_rgb('#83c193'))
            init_color(7, *hex_to_rgb('#e7dcc4'))
            init_color(8, *hex_to_rgb('#45525c'))
            # init_color(9, *hex_to_rgb('#ed9294'))
            # init_color(10, *hex_to_rgb('#b0ce7b'))
            # init_color(11, *hex_to_rgb('#edc77a'))
            # init_color(12, *hex_to_rgb('#7ac9c0'))
            # init_color(13, *hex_to_rgb('#e5a7c4'))
            # init_color(14, *hex_to_rgb('#7dd903'))
            # init_color(15, *hex_to_rgb('#b2a790'))
            init_color(12, *hex_to_rgb('#7ac9c0'))

            c.curs_set(0)
            init_pair(1, 7, 8) # Default
            init_pair(2, 4, 8) # Ok/Reset Buttons
            init_pair(3, 0, 12) # Highlight
            init_pair(4, 1, 12) # Error
            init_pair(5, 0, 6) # Sucess Message

            c.set_escdelay(5)
        else:
            use_default_colors()

def stdscr_init(stdscr:window, wp:WinProps):
    stdscr.clear()
    stdscr.resize(wp.lines, wp.cols)
    stdscr.mvwin(wp.marginy, wp.marginx)
    stdscr.bkgd(ord(' ') | color(1))
    stdscr.attrset(color(2))
    stdscr.border()
    stdscr.attrset(0)
    stdscr.refresh()

def inner_init(inner:window, innerp:WinProps) -> None:
    inner.setscrreg(1, innerp.lines)
    inner.scrollok(True)
    inner.move(1,1)
    inner.refresh()
