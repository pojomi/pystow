# pystow

A terminal UI for managing dotfile symlinks. Select packages from your dotfiles repository and pystow will create the corresponding symlinks in your home directory. Directory structure mimics that of GNU Stow.

## Requirements

- Python 3.10+
- PyInstaller (optional)

## Usage

```
python pystow.py /path/to/dotfiles
```
pystow lists every top-level directory in your dotfiles repository (excluding `.git`). Navigate the list, select the packages you want to install, then press `<OK>` to create the symlinks.

## Installation

From root directory of repo:
```
pyinstaller --onefile --name pystow pystow.py
sudo cp dist/pystow /usr/local/bin # Or your preferred bin path

pystow /path/to/dotfiles
```



## Directory structure

Each package directory must contain exactly one subdirectory. That subdirectory name determines where the symlink is placed under `$HOME`:

```
dotfiles/
  nvim/
    .config/        # symlink created at ~/.config/nvim
      init.lua
  bash/
    .config/        # symlink created at ~/.config/bash
      bashrc
```

pystow creates: `~/<subdir>/<package> -> <dotfiles>/<package>/<subdir>`

If the destination path already exists, the package is skipped and an error is shown inline.

## Key bindings

| Key | Action |
|-----|--------|
| `j` / `Down` / `Ctrl+N` | Move selection down |
| `k` / `Up` / `Ctrl+P` | Move selection up |
| `Space` | Select / deselect item |
| `Tab` / `l` / `h` | Cycle button focus |
| `Enter` | Confirm focused button |
| `Esc` | Deselect focused button |
| `q` | Quit |
| `?` | Show key binding help |
