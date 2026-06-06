import os
from os import path as p
from curses import color_pair as color, window
from classes import Dirs, WinProps, Button

_HELP_BINDINGS: list[tuple[str, str]] = [
    ("j / Down / ^N", "Move down"),
    ("k / Up   / ^P", "Move up"),
    ("Space",         "Select / deselect item"),
    ("Tab / l / h",   "Cycle button focus"),
    ("Enter",         "Confirm / execute action"),
    ("Esc",           "Deselect focused button"),
    ("q",             "Quit"),
    ("?",             "Show this help"),
]

def _show_help(stdscr: window, inner: window, innerp: WinProps) -> None:
    key_w  = max(len(k) for k, _ in _HELP_BINDINGS)
    desc_w = max(len(d) for _, d in _HELP_BINDINGS)
    w = key_w + desc_w + 6   # 2 border + 2 pad + 2 gap between columns
    h = len(_HELP_BINDINGS) + 5  # top border + title + blank + bindings + dismiss + bottom border

    y = max(0, (innerp.lines - h) // 2)
    x = max(0, (innerp.cols  - w) // 2)

    try:
        hw = inner.derwin(h, w, y, x)
    except Exception:
        return

    hw.bkgd(ord(' ') | color(1))
    hw.erase()
    hw.border()

    title = "Key Bindings"
    hw.addstr(1, (w - len(title)) // 2, title, color(2))

    for i, (key, desc) in enumerate(_HELP_BINDINGS):
        hw.addstr(3 + i, 2, f"{key:<{key_w}}", color(2))
        hw.addstr(3 + i, 2 + key_w + 2, desc, color(1))

    dismiss = "[ any key to close ]"
    hw.addstr(h - 2, (w - len(dismiss)) // 2, dismiss, color(1))

    hw.refresh()
    while True:
        key = stdscr.getkey()
        if key:
            hw.clear()
            del hw
            inner.touchwin()
            inner.refresh()
            break

def _loop(dirs:Dirs, stdscr:window, inner:window, innerp:WinProps, ok:Button, reset:Button) -> None:
    # Track focused row
    l:int = 0
    # Main loop
    while True:
        key:str = stdscr.getkey()
        match key:
            case "q":
                break
            case "j" | "KEY_DOWN" | "":
                l = inner.getyx()[0]
                # Move highlighted selection down by 1
                if l < dirs.count and l < innerp.lines:
                    inner.chgat(l,1, color(1))
                    l+=1
                    dirs.highlighted+=1

                    inner.move(l, 2)
                    inner.chgat(l, 1, color(3))
                    inner.refresh()
                # Scroll if not all shown
                elif l == innerp.lines and dirs.count > innerp.lines and dirs.shown_range[1] < dirs.count:
                    inner.scroll()
                    inner.chgat(l-1, 1, color(1))

                    # Only increment up to last accessible row
                    if dirs.highlighted + 1 <= dirs.count:
                        dirs.highlighted+=1


                    if dirs.dots[dirs.highlighted] not in dirs.selected:
                        inner.addstr(l, 1, f'[ ]{dirs.dots[dirs.shown_range[1]]}')
                    else:
                        inner.addstr(l, 1, f'[*]{dirs.dots[dirs.shown_range[1]]}')

                    dirs.incr_range()

                    inner.chgat(l, 1, color(3))
                    stdscr.attrset(color(2))
                    stdscr.border() # Needs to be called as scrolling erases it
                                    # on that row
                    stdscr.attrset(color(0))
                    stdscr.refresh()
                    inner.refresh()
                elif l == innerp.lines and not ok.is_focused or reset.is_focused:
                    inner.chgat(l, 1, color(1))
                    inner.chgat(innerp.bottom_margin, ok.start_pos, ok.label_len, color(3))
                    ok.is_focused = True
                    inner.refresh()

            case "k" | "KEY_UP" | "":

                if ok.is_focused or reset.is_focused and isinstance(l, int):
                    ok.is_focused = False
                    reset.is_focused = False

                    inner.chgat(innerp.bottom_margin, 1, color(1))
                    inner.chgat(dirs.shown_range[1] if l > 0 else 1, 1, color(3))
                    dirs.highlighted = dirs.shown_range[1]-1
                    inner.refresh()
                    continue

                l = inner.getyx()[0]
                if l > 1:
                    inner.chgat(l,1, color(1))
                    l-=1
                    dirs.highlighted-=1

                    inner.move(l, 2)
                    inner.chgat(l,1, color(3))
                    inner.refresh()
                # Scroll if not all shown
                elif l == 1 and dirs.shown_range[0] > 0:
                    inner.scroll(-1)
                    inner.chgat(l+1, 1, color(1))
                    dirs.decr_range()


                    if dirs.highlighted - 1 >= 0 and not (ok.is_focused or reset.is_focused):
                        dirs.highlighted-=1

                    if dirs.dots[dirs.highlighted] not in dirs.selected:
                        inner.addstr(l, 1, f'[ ]{dirs.dots[dirs.shown_range[0]]}')
                    else:
                        inner.addstr(l, 1, f'[*]{dirs.dots[dirs.shown_range[0]]}')

                    inner.chgat(l, 1, color(3))
                    stdscr.border()
                    stdscr.refresh()
                    inner.refresh()
            case " ":
                # Unselect the row if it's found in dirs.selected
                if not ok.is_focused and not reset.is_focused:
                    l = inner.getyx()[0]
                    # Draw default unselected row and clear from cursor to EOL
                    # to fully reset. Remove row from dirs.selected
                    if dirs.dots[dirs.highlighted] in dirs.selected:
                        inner.addstr(l, 1, f'[ ]{dirs.dots[dirs.highlighted]}', color(3))
                        inner.clrtoeol()
                        inner.chgat(color(3))
                        dirs.selected.remove(dirs.dots[dirs.highlighted])
                        dirs.link_dest.remove(dirs.dest_ref[dirs.highlighted])
                        if dirs.src_ref[dirs.highlighted] in dirs.link_src:
                            dirs.link_src.remove(dirs.src_ref[dirs.highlighted])
                    # Handle adding new selection
                    else:
                        # Returns True if directory does not exist
                        # Add selection '*', and append symlink reference
                        if len(dirs.dest_ref[dirs.highlighted]) > 1:
                            dirs.link_dest.append(dirs.dest_ref[dirs.highlighted])
                            dirs.link_src.append(dirs.src_ref[dirs.highlighted])
                            dirs.selected.append(dirs.dots[dirs.highlighted])
                            inner.addch(l, 2, '*', color(3))
                            inner.addstr(l, dirs.longest, f'-> {dirs.link_dest[-1]}', color(3))
                        # Redraw same line but append error message
                        else:
                            if dirs.dest_ref[dirs.highlighted] == 'f':
                                inner.addstr(l, dirs.longest, 'File already exists', color(4))
                            elif dirs.dest_ref[dirs.highlighted] == 'd':
                                inner.addstr(l, dirs.longest, 'Directory already exists', color(4))

                    inner.refresh()
            case "\t" | "l" | "h" | "" | "":
                # Clear row highlighting
                if not ok.is_focused and not reset.is_focused:
                    l = inner.getyx()[0]
                    inner.chgat(l, 1, color(1))
                    inner.chgat(innerp.bottom_margin, ok.start_pos, ok.label_len, color(3))
                    ok.is_focused = True
                    inner.refresh()

                elif reset.is_focused:
                    # Clear any highlight from reset button
                    inner.chgat(innerp.bottom_margin, reset.start_pos, reset.label_len, color(1))
                    inner.chgat(innerp.bottom_margin, ok.start_pos, ok.label_len, color(3))
                    ok.is_focused = True
                    reset.is_focused = False
                    inner.refresh()

                elif ok.is_focused:
                    # Clear any highlight from ok button
                    inner.chgat(innerp.bottom_margin, ok.start_pos, ok.label_len, color(1))
                    inner.chgat(innerp.bottom_margin, reset.start_pos, reset.label_len, color(3))
                    ok.is_focused = False
                    reset.is_focused = True
                    inner.refresh()
                else:
                    pass
            case "\x1b":
                # Escape back to previous location
                if ok.is_focused or reset.is_focused:
                    inner.chgat(innerp.bottom_margin, 1, color(1))
                    ok.is_focused = False
                    reset.is_focused = False
                    # Need to check if we scrolled "into" the button or not
                    # Subtract 1 if we did. Highlights the margin otherwise
                    inner.chgat(l, 1, color(3))
                    inner.refresh()
                else:
                    pass
            case "\n":
                if reset.is_focused:
                    i:int = 1
                    inner.chgat(innerp.bottom_margin, 1, color(1))
                    for r in dirs.dots[dirs.shown_range[0]:dirs.shown_range[1]-dirs.shown_range[0]]:
                        inner.addstr(i, 1, f'[ ]{r}', color(1))
                        inner.clrtoeol()
                        inner.chgat(color(1))
                        i+=1
                    dirs.selected.clear()
                    inner.chgat(1, 1, color(3))
                    dirs.highlighted = 0
                    reset.is_focused = False
                    l = 1
                    inner.refresh()
                if ok.is_focused:
                        try:
                            for sym,dst in zip(dirs.link_src, dirs.link_dest):
                                # This should always succeed since paths are filtered
                                # when selections are made
                                os.symlink(sym, dst)
                        except OSError as e:
                            print(e.strerror)
                        else:
                            success_msg:str = f'Success: {len(dirs.link_src)} links created'
                            start_point = innerp.cols // 2 - len(success_msg) // 2
                            inner.addstr(innerp.bottom_margin-1, start_point, success_msg, color(5))
                            ok.is_focused = False
                            dirs.selected.clear()
                            dirs.link_dest.clear()
                            l = 1
                            inner.refresh()
            case "?":
                _show_help(stdscr, inner, innerp)
            case _:
                pass
