#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GdkPixbuf
from xdg import BaseDirectory

import os
import json
import sys


__appname__ = 'pappymenu'
__version__ = (0, 1)
__source__ = 'http://github.com/Kingdread/pappymenu'

command_string = None


def cache_path():
    """Return the path of the cache file."""
    return os.path.join(BaseDirectory.save_cache_path(__appname__),
                        'menu-cache')


def regenerate_cache(path):
    """Regenerate the cache file at the given path."""
    # Yes, we could use xdg.Menu here, but it seems to error when
    # 'applications.menu' is not found. Therefore, we use the external tool
    # 'xdg_menu', which doesn't care and correctly scans
    # /usr/share/applications ($XDG_DATA_DIR/applications) without worrying
    # about missing files. In the future though, we might switch.
    
    # The openbox3 format seems nice to parse as XML and contains the icon, so
    # no need to write a new custom parser.

    # The cache format is a simple json document in the following structure:
    # {
    #     'menu_name':
    #         ('/menu/icon.png',
    #          {
    #             'app_name': ('/app/icon.png', 'app-command'),
    #             ...
    #          }),
    #      ...
    # }

    # Importing here to save time if we don't need to regenerate the cache
    import subprocess
    from lxml import etree

    try:
        menu_xml = subprocess.check_output(['xdg_menu', '--format',
                                            'openbox3-pipe'])
    except FileNotFoundError:
        print("Please install xdg_menu for {} to work!".format(__appname__),
              file=sys.stderr)
        sys.exit(1)
    # Valid xml needs a root element
    menu = etree.fromstring(menu_xml)
    result = {}
    for menu in menu.xpath('//openbox_pipe_menu/menu'):
        menu_name = menu.attrib['label']
        menu_icon = menu.get('icon', '')
        programs = {}
        for app in menu.findall('item'):
            app_name = app.attrib['label']
            app_icon = app.get('icon', '')
            app_command = ''.join(app.itertext()).strip()
            programs[app_name] = (app_icon, app_command)
        result[menu_name] = (menu_icon, programs)

    # Save the cache
    with open(path, 'w') as output_file:
        json.dump(result, output_file)

    return result


def get_menu_data():
    """Returns a dict of Name->Submenu entries."""
    path = cache_path()
    if not os.path.isfile(path):
        return regenerate_cache(path)

    # Load the cache
    with open(path) as input_file:
        return json.load(input_file)


def icon_item(icon_filename, label, icon_size=(16, 16)):
    """Return a Gtk.MenuItem with the given icon and label set."""
    item = Gtk.MenuItem()
    box = Gtk.HBox()
    box.set_halign(Gtk.Align.START)
    box.set_spacing(5)
    
    width, height = icon_size
    if icon_filename:
        icon_buf = GdkPixbuf.Pixbuf.new_from_file(icon_filename)
        icon = Gtk.Image.new_from_pixbuf(icon_buf.scale_simple(width, height, GdkPixbuf.InterpType.HYPER))
    else:
        # Aligning the text by providing an empty icon
        icon_buf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, width, height)
        # Fill with transparent black
        icon_buf.fill(0)
        icon = Gtk.Image.new_from_pixbuf(icon_buf)

    icon.show()
    box.add(icon)
    lbl = Gtk.Label(label)
    lbl.show()
    box.add(lbl)
    box.show()
    item.add(box)
    item.show()
    return item


def make_menu():
    root_menu = Gtk.Menu()
    menu_data = get_menu_data()

    for category, content in sorted(menu_data.items()):
        category_icon, programs = content

        menu = icon_item(category_icon, category)
        submenu = Gtk.Menu()
        for program, content in sorted(programs.items()):
            program_icon, program_cmd = content

            item = icon_item(program_icon, program)
            item.connect('activate', set_command, program_cmd)
            submenu.append(item)

        menu.set_submenu(submenu)
        root_menu.append(menu)

    return root_menu


def set_command(widget, cmd_string):
    """Set the command to execute and quit gtk."""
    global command_string
    command_string = cmd_string
    Gtk.main_quit()


if '-h' in sys.argv:
    print("""Usage: {executable} [-h | -v | -r]

{app} is an application-launcher that (compared to dmenu &c) provides a
graphical list of installed applications. {app} uses xdg_menu under the hood to
generate the menu entries. Calling {executable} without arguments will provide
the menu at the mouse pointer location. Select a program to start it, press
<Esc> to cancel.

Available options are:
    -h\tShow this help.
    -v\tShow the version.
    -r\tRegenerate the cache at {cache}. This is automatically done when the
      \tcache doesn't yet exist.
""".format(executable=sys.argv[0], app=__appname__, cache=cache_path()))
elif '-v' in sys.argv:
    print("{} version {}.\n(c) by Daniel Schadt.\n{}".format(
        __appname__, '.'.join(map(str, __version__)), __source__))
elif '-r' in sys.argv:
    print("Regenerating menu cache...")
    regenerate_cache(cache_path())
    print("Cache saved.")
else:
    menu = make_menu()
    menu.connect('cancel', Gtk.main_quit)
    menu.connect('deactivate', Gtk.main_quit)
    # A bit of a "dirty hack", having a menu popup without a widget or a button...
    menu.popup(None, None, None, None, 0, 0)

    Gtk.main()

    # Execute the menu action, if one was selected
    if command_string:
        import shlex
        args = shlex.split(command_string)
        os.execvp(args[0], args)
