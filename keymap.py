import os
from curses import color_pair as color, window
from classes import Dir, WinProps, Button

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

def loop(dir:Dir, stdscr:window, inner:window, innerp:WinProps, ok:Button, reset:Button) -> None:
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
                if l < dir.count and l < innerp.lines:
                    inner.chgat(l,1, color(1))
                    l+=1
                    dir.highlighted+=1

                    inner.move(l, 2)
                    inner.chgat(l, 1, color(3))
                    inner.refresh()
                # Scroll if not all shown
                elif l == innerp.lines and dir.count > innerp.lines and dir.shown_range[1] < dir.count:
                    inner.scroll()
                    inner.chgat(l-1, 1, color(1))

                    # Only increment up to last accessible row
                    if dir.highlighted + 1 <= dir.count:
                        dir.highlighted+=1


                    if not dir.selected_indexes.index(dir.highlighted):
                        inner.addstr(l, 1, f'[ ]{dir.dot_tree[dir.shown_range[1]][1]}')
                    else:
                        inner.addstr(l, 1, f'[*]{dir.dot_tree[dir.shown_range[1]][1]}')

                    dir.incr_range()

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

                if ok.is_focused or reset.is_focused:
                    ok.is_focused = False
                    reset.is_focused = False

                    inner.chgat(innerp.bottom_margin, 1, color(1))
                    inner.chgat(dir.shown_range[1] if l > 0 else 1, 1, color(3))
                    dir.highlighted = dir.shown_range[1]-1
                    inner.refresh()
                    continue

                l = inner.getyx()[0]
                if l > 1:
                    inner.chgat(l,1, color(1))
                    l-=1
                    dir.highlighted-=1

                    inner.move(l, 2)
                    inner.chgat(l,1, color(3))
                    inner.refresh()
                # Scroll if not all shown
                elif l == 1 and dir.shown_range[0] > 0:
                    inner.scroll(-1)
                    inner.chgat(l+1, 1, color(1))
                    dir.decr_range()


                    if dir.highlighted - 1 >= 0 and not (ok.is_focused or reset.is_focused):
                        dir.highlighted-=1

                    if not dir.selected_indexes.index(dir.highlighted):
                        inner.addstr(l, 1, f'[ ]{dir.dot_tree[dir.shown_range[0]][1]}')
                    else:
                        inner.addstr(l, 1, f'[*]{dir.dot_tree[dir.shown_range[0]][1]}')

                    inner.chgat(l, 1, color(3))
                    stdscr.border()
                    stdscr.refresh()
                    inner.refresh()
            case " ":
                # Unselect the row if it's found in dir.selected
                if not ok.is_focused and not reset.is_focused:
                    l = inner.getyx()[0]
                    # Draw default unselected row and clear from cursor to EOL
                    # to fully reset. Remove row from dir.selected
                    if dir.dot_tree.index(dir.highlighted) in dir.selected_indexes:
                        inner.addstr(l, 1, f'[ ]{dir.dot_tree[dir.highlighted][1]}', color(3))
                        inner.clrtoeol()
                        inner.chgat(color(3))
                        dir.selected_indexes.remove(dir.highlighted)
                    # Handle adding new selection
                        # Redraw same line but append error message
                    elif os.path.exists(dir.link_path[dir.highlighted]):
                        inner.addstr(l, dir.longest, 'Already exists', color(4))
                    else:
                        # Returns True if directory does not exist
                        # Add selection '*', and append symlink reference
                        dir.selected_indexes.append(dir.highlighted)
                        inner.addch(l, 2, '*', color(3))
                        inner.addstr(l, dir.longest, f'-> {dir.link_path[dir.highlighted]}', color(3))

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
                    for r in dir.dot_tree[dir.shown_range[0]:dir.shown_range[1]-dir.shown_range[0]][1]:
                        inner.addstr(i, 1, f'[ ]{r}', color(1))
                        inner.clrtoeol()
                        inner.chgat(color(1))
                        i+=1
                    dir.selected_indexes.clear()
                    inner.chgat(1, 1, color(3))
                    dir.highlighted = 0
                    reset.is_focused = False
                    l = 1
                    inner.refresh()
                if ok.is_focused:
                        try:
                            for i in dir.selected_indexes:
                                os.symlink(dir.dot_subtree[i][0],dir.link_path[i])
                        except OSError as e:
                            print(e.strerror)
                        else:
                            success_msg:str = f'Success: {len(dir.selected_indexes)} links created'
                            start_point = innerp.cols // 2 - len(success_msg) // 2
                            inner.addstr(innerp.bottom_margin-1, start_point, success_msg, color(5))
                            ok.is_focused = False
                            dir.selected_indexes.clear()
                            l = 1
                            inner.refresh()
            case "?":
                _show_help(stdscr, inner, innerp)
            case _:
                pass
