# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from gi.repository import Gtk
from gi.repository import Gdk
import locale
import logging
from glob import glob

from sugar3.activity.activity import get_bundle_path

import theme

logger = logging.getLogger('flipsticks')

THEMES = []

class Lesson:
    def __init__(self, index, filename):
        self.index = index
        self.name = os.path.splitext(os.path.basename(filename).lstrip(
                '.-_1234567890').replace('_', ' '))[0]
        self.text = file(filename, 'r').read()

    def change(self):
        View.notebook.set_current_page(self.index)

class View(Gtk.EventBox):
    notebook = None

    def __init__(self):
        Gtk.EventBox.__init__(self)

        View.notebook = Gtk.Notebook()
        View.notebook.props.show_border = False
        View.notebook.props.show_tabs = False
        self.add(View.notebook)

        for i in THEMES:
            view = Gtk.TextView()
            view.get_buffer().set_text(i.text)
            view.set_wrap_mode(Gtk.WRAP_WORD)
            view.set_editable(False)

            view_box = Gtk.EventBox()
            view_box.add(view)
            view_box.modify_bg(Gtk.STATE_NORMAL, Gdk.Color.parse(theme.WHITE))
            view_box.props.border_width = 10

            border_box = Gtk.EventBox()
            border_box.add(view_box)
            border_box.modify_bg(Gtk.STATE_NORMAL, Gdk.Color.parse(theme.WHITE))

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scrolled_window.add_with_viewport(border_box)

            View.notebook.append_page(scrolled_window)

        self.show_all()

_lessons_dir = os.path.join(get_bundle_path(), 'lessons')
_lang = locale.getdefaultlocale()[0].split('_')[0]

if not os.path.isdir(os.path.join(_lessons_dir, _lang)):
    logger.info('Cannot find lessons for language %s, thus use en' % _lang)
    _lang = 'en'

for i, filename in enumerate(sorted(glob(os.path.join(_lessons_dir, _lang, '*')))):
    THEMES.append(Lesson(i, filename))
