`pappymenu` is an application launcher that (unlike `dmenu_run` and Co.)
provides a graphical list of installed applications, according to
XDG-standards. It reads desktop entries from `$XDG_DATA_DIR/applications`
(actually, it uses `xdg_menu` to do this) and builds a nice application
launcher, like the GNOME2-applications-menu.

![Screenshot](/screenshot.png?raw=true)

Why?
----

I usually use `dmenu_run` to launch my applications. But there are some
programs that I rarely use and forget the command (or even the application
name). `pappymenu` provides help in those cases by giving me a launcher similar
to the application menu found in other DEs (Mate, Xfce, ...).

How?
----

`pappymenu` uses `xdg_menu` under the hood to generate the menu list. It then
displays a menu with Gtk3 and upon selecting an entry, it replaces itself with
the given command (by calling `exec`).

Requirements
------------

- Python 3+
- [xdg\_menu](https://wiki.archlinux.org/index.php/Xdg-menu) in your $PATH
- GObject3 bindings for Python 3 (Package `python-gobject` in Arch,
  `python3-gi` in Ubuntu)

Installation
------------

Make sure you have the requirements installed.

Copy `pappymenu.py` somewhere where you can find it. Run it without arguments
to get the menu.

You can bind a key combination to spawn pappymenu, example for herbstluftwm:

    herbstclient keybind Mod4-Shift-d spawn ~/src/pappymenu/pappymenu.py

Updating the menu
-----------------

If you install new applications, it might be required to update the menu cache
(usually `~/.cache/pappymenu/menu-cache`). This can be achieved by running
pappymenu with the `-r` flag, e.g. `pappymenu.py -r`. The cache will be updated
and saved.

License
-------

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along
    with this program.  If not, see <http://www.gnu.org/licenses/>.
