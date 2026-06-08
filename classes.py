import os
from os import path as p
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

class Dirs:
    def __init__(self, rootdir:str):
        self.root:str = rootdir
        self.home:str
        self.dots:list[str]
        try:
            self.home = os.getenv('HOME')  # type: ignore
        except (TypeError, AttributeError) as e:
            raise RuntimeError('Failed to get HOME environment variable') from e

        _,self.dots,_ = next(os.walk(self.root))
        self.dots.remove('.git')

        self.link_src:list[str] = [] # Full paths to source dotfiles
        self.link_dest:list[str] = [] # Full paths to selected symlink destinations
        self.dest_ref:list[str] = [] # References to destination paths for linking
        self.src_ref:list[str] = [] # References to source paths for linking
        for d in self.dots:
            root,dir,file = next(os.walk(p.join(self.root, d)))
            if len(dir) > 0:
                self.src_ref.append(p.join(root, dir[0]))
                home_path_as_dir = p.join(self.home, dir[0], d)
                if p.exists(home_path_as_dir):
                    self.dest_ref.append('d')
                else:
                    self.dest_ref.append(home_path_as_dir)
            elif len(file) == 1 and len(dir) == 0:
                home_path_as_file = p.join(self.home, d, file[0])
                self.src_ref.append(p.join(self.root, d, file[0]))
                if p.exists(home_path_as_file):
                    self.dest_ref.append('f')
                else:
                    self.dest_ref.append(home_path_as_file)

        self.longest:int = len(max(self.dots, key=len))+5
        self.count:int = len(self.dots)
        self.shown_range:list[int] = []
        # Tracker for cursor-index relationship
        # Calculate by comparing index to line, add if gt visible rows
        self.highlighted:int = 0
        self.selected:list[str] = []


    def add_src(self, path:str) -> bool:
        index:int = self.dots.index(path)

        self.link_src.append(self.src_ref[index])
        return True

    def add_dest(self, path:str) -> bool:
        index:int = self.dots.index(path)

        if len(self.dest_ref[index]) > 1:
            self.link_dest.append(self.dest_ref[index])
            self.selected.append(path)
            return True
        else:
            return False


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
