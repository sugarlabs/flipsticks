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

import gtk
from gettext import gettext as _

from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.graphics.toolbutton import ToolButton

from toolkit.activity import SharedActivity
from toolkit.temposlider import TempoSlider
from toolkit.toolbarbox import ToolbarBox
from toolkit.activity_widgets import *

import model
import montage
import lessons
from messenger import Messenger, SERVICE
from theme import *

class flipsticksActivity(SharedActivity):
    def __init__(self, handle):
        self.notebook = gtk.Notebook()
        SharedActivity.__init__(self, self.notebook, SERVICE, handle)

        self.notebook.show()
        self.notebook.props.show_border = False
        self.notebook.props.show_tabs = False

        self.montage = montage.View(self)
        self.notebook.append_page(self.montage)
        self.lessons = lessons.View()
        self.lessons.show()
        self.notebook.append_page(self.lessons)

        toolbox = ToolbarBox()
        toolbox.show()

        toolbox.toolbar.insert(ActivityToolbarButton(self), -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        toolbox.toolbar.insert(separator, -1)

        lessons_button = ToggleToolButton('mamamedia')
        lessons_button.connect('toggled', self.__toggled_lessons_button_cb)
        lessons_button.set_tooltip(_('Lessons'))
        toolbox.toolbar.insert(lessons_button, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        toolbox.toolbar.insert(separator, -1)

        self.notebook_toolbar = gtk.Notebook()
        self.notebook_toolbar.props.show_border = False
        self.notebook_toolbar.props.show_tabs = False
        self.notebook_toolbar.append_page(MontageToolbar(self.montage))
        self.notebook_toolbar.append_page(LessonsToolbar())
        self.notebook_toolbar.show()

        notebook_item = gtk.ToolItem()
        notebook_item.set_expand(True)
        notebook_item.add(self.notebook_toolbar)
        notebook_item.show()
        toolbox.toolbar.insert(notebook_item, -1)

        toolbox.toolbar.insert(StopButton(self), -1)

        toolbox.show_all()
        self.toolbar_box = toolbox

    def resume_instance(self, filepath):
        model.load(filepath)
        self.montage.restore()

    def save_instance(self, filepath):
        model.save(filepath)

    def share_instance(self, tube_conn, initiating):
        self.messenger = Messenger(tube_conn, initiating, self.montage)

    def __toggled_lessons_button_cb(self, button):
        page = button.props.active and 1 or 0
        self.notebook_toolbar.set_current_page(page)
        self.notebook.set_current_page(page)

class MontageToolbar(gtk.Toolbar):
    def __init__(self, montage):
        gtk.Toolbar.__init__(self)
        self.montage = montage

        # edit buttons

        setframe = ToolButton('dialog-ok')
        setframe.connect('clicked', self._setframe_cb)
        setframe.set_tooltip(_('Set frame'))
        self.insert(setframe, -1)

        clearframe = ToolButton('gtk-delete')
        clearframe.connect('clicked', self._clearframe_cb)
        clearframe.set_tooltip(_('Clear frame'))
        self.insert(clearframe, -1)

        resetframe = ToolButton('gtk-cancel')
        resetframe.connect('clicked', self._resetframe_cb)
        resetframe.set_tooltip(_('Reset'))
        self.insert(resetframe, -1)

        separator = gtk.SeparatorToolItem()
        self.insert(separator,-1)

        # play/pause buttons

        play_img_1 = gtk.Image()
        play_img_1.set_from_icon_name('media-playback-start-back',
                gtk.ICON_SIZE_LARGE_TOOLBAR)
        pause_img_1 = gtk.Image()
        pause_img_1.set_from_icon_name('media-playback-pause',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        play_img_2 = gtk.Image()
        play_img_2.set_from_icon_name('media-playback-start',
                gtk.ICON_SIZE_LARGE_TOOLBAR)
        pause_img_2 = gtk.Image()
        pause_img_2.set_from_icon_name('media-playback-pause',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        paly_1 = ToggleToolButton('media-playback-start-back')
        play_2 = ToggleToolButton('media-playback-start')

        paly_1.connect('toggled', self._play_cb,
                (paly_1, play_2), (play_img_1, pause_img_1),
                self.montage.playbackwards)
        self.insert(paly_1, -1)
        paly_1.set_tooltip(_('Play backward / Pause'))

        play_2.connect('toggled', self._play_cb,
                (play_2, paly_1), (play_img_2, pause_img_2),
                self.montage.playforwards)
        self.insert(play_2, -1)
        play_2.set_tooltip(_('Play forward / Pause'))

        # tempo button

        tempo = TempoSlider(0, 99)
        tempo.adjustment.connect("value-changed", self._tempo_cb)
        tempo.set_size_request(250, -1)
        tempo.set_value(50)
        tempo_item = gtk.ToolItem()
        tempo_item.add(tempo)
        self.insert(tempo_item, -1)

        separator = gtk.SeparatorToolItem()
        self.insert(separator,-1)

        # export buttons

        exportframe = ToolButton('image')
        exportframe.connect('clicked', self._exportframe_cb)
        exportframe.set_tooltip(_('Snapshot'))
        self.insert(exportframe, -1)

        self.show_all()

    def _exportframe_cb(self, widget):
        self.montage.exportframe()

    def _setframe_cb(self, widget):
        self.montage.setframe()

    def _clearframe_cb(self, widget):
        self.montage.clearframe()

    def _resetframe_cb(self, widget):
        self.montage.reset()

    def _tempo_cb(self, widget):
        self.montage.setplayspeed(widget.value)

    def _play_cb(self, widget, buttons, images, play):
        if widget.get_active():
            buttons[1].set_active(False)
            images[1].show()
            widget.set_icon_widget(images[1])
            play()
        else:
            images[0].show()
            widget.set_icon_widget(images[0])
            self.montage.stop()

class LessonsToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)
        self._mask = False

        for lesson in lessons.THEMES:
            button = gtk.ToggleToolButton()
            button.set_label(lesson.name)
            button.connect('clicked', self._lessons_cb, lesson)
            self.insert(button, -1)

        self.get_nth_item(0).set_active(True)
        self.show_all()

    def _lessons_cb(self, widget, lesson):
        if self._mask:
            return
        self._mask = True

        for i, j in enumerate(lessons.THEMES):
            if j != lesson:
                self.get_nth_item(i).set_active(False)

        widget.props.active = True
        lesson.change()
        self._mask = False
