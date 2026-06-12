import os
from os import path as p
import sys
import curses
from curses import wrapper, window, color_pair as color
from classes import Button, Dir, WinProps
import keymap, manage_windows

def main(stdscr:window, dots:str):
    if not hasattr(os, 'symlink'):
        raise OSError('os.symlink() is not supported on this system')

    # Tty screen initialization
    manage_windows.stdscr_setup()

    stdp:WinProps = WinProps(stdscr, True)

    manage_windows.stdscr_init(stdscr, stdp)

    inner:window = stdscr.derwin(stdp.lines - 2, stdp.cols - 2, 0, 0)
    innerp:WinProps = WinProps(inner, False)

    manage_windows.inner_init(inner, innerp)

    # Primary class for all file path management
    dirs:Dir

    if p.exists(dots):
        dirs = Dir(dots)
    else:
        raise TypeError(f'Invalid path: {dots}')

    pos:int = 1

    # Draw initial screen -- Either all contents or max inner_lines
    try:
        for d in dirs.dot_tree[0:innerp.lines] if dirs.count >= innerp.lines else dirs.dot_tree:
            inner.addstr(pos, 1, f'[ ]{d[1]}', color(1))
            pos+=1

        dirs.shown_range = [0, pos-1]
    except curses.error as e:
        raise e

    # Draw buttons on bottom line
    ok = Button('<OK>', innerp.bottom_margin, innerp.cols, True)
    reset = Button('<Reset>', innerp.bottom_margin, innerp.cols, False)

    # Draw buttons
    try:
        inner.addstr(innerp.bottom_margin, ok.start_pos, ok.label, color(1))
        inner.addstr(innerp.bottom_margin, reset.start_pos, reset.label, color(1))

        # Move back to top and init
        inner.move(1,1)
        inner.chgat(1,1, color(3))
        inner.refresh()

        keymap.loop(dirs, stdscr, inner, innerp, ok, reset)
    except curses.error as e:
        raise e

if len(sys.argv) != 2:
    raise TypeError('Usage: pystow <path>')

wrapper(main, sys.argv[1])
