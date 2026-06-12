import os
from os import path as p
from typing import cast
from curses import window

class WinProps:
    def __init__(self, win:window, is_root:bool):
        self.lines:int
        self.cols:int
        self.lines,self.cols = win.getmaxyx()
        self.marginy:int = round((self.lines*0.1)/2)
        self.marginx:int = round((self.cols*0.1)/2)
        if is_root:
            self.lines = round(self.lines * 0.9)
            self.cols = round(self.cols * 0.9)
        else:
            self.lines-=2

        self.bottom_margin:int = self.lines-1

class Dir:
    def __init__(self, rootdir:str):
        self.root:str = rootdir
        self.home:str
        # self.dots:dict[str, list[str] | str] = {}

        try:
            self.home = cast(str, os.getenv('HOME'))  # type: ignore
        except (TypeError, AttributeError) as e:
            raise RuntimeError('Failed to get HOME environment variable') from e

        self.dot_tree:tuple[str, list[str], list[str]] = next(os.walk(self.root))
        self.dot_tree[1].remove('.git')
        # (~/dotfiles/dotname, [dir], [file])
        self.dot_subtree:list[tuple[str, list[str], list[str]]] = [ 
            next(os.walk(p.join(self.dot_tree[0], d))) for d in self.dot_tree[1]
        ]

        self.link:list[str] = []
        for i in range(len(self.dot_tree[1])):
            # ~/basedir/dir
            if len(self.dot_subtree[i][1]) > 0 and len(self.dot_subtree[i][2]) == 0:
                if self.dot_tree[1][i] != self.dot_subtree[i][1][0]:
                    self.link.append(p.join(self.home,self.dot_subtree[i][1][0],self.dot_tree[1][i]))
                # ~/dir --- example ~/Documents
                else:
                    self.link.append(p.join(self.home,self.dot_tree[1][i]))
            # ~/file
            elif len(self.dot_subtree[i][2]) > 0 and len(self.dot_subtree[i][1]) == 0:
                self.link.append(p.join(self.home,self.dot_subtree[i][2][0]))

        self.selected_indexes:list[int] = []

        self.longest:int = len(max(self.dot_tree, key=lambda k: k[1] if k else ''))+5 
        self.count:int = len(self.dot_tree[1])
        self.shown_range:list[int] = []
        # Tracker for cursor-index relationship
        # Calculate by comparing index to line, add if gt visible rows
        self.highlighted:int = 0


    def incr_range(self) -> None:
       self.shown_range[0]+=1
       self.shown_range[1]+=1

    def decr_range(self) -> None:
        self.shown_range[0]-=1
        self.shown_range[1]-=1

class Button:
    def __init__(self, label:str, row:int, col_count:int, left:bool):
        self.is_focused:bool = False
        self.label:str = label
        self.label_len:int = len(self.label)
        self.row:int = row
        self.cols:int = col_count
        self.row_center:int = self.cols // 2
        self.start_pos:int
        if left:
            self.start_pos = self.row_center - 5 - len(self.label)
        else:
            self.start_pos = self.row_center + 5
