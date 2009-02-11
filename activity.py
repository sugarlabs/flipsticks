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
import gtk
from sugar.activity import activity
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection
import telepathy
import telepathy.client
from dbus import Interface
from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

import model
from theme import *
from flipsticks import flipsticks

class flipsticksActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self,handle)
        bundle_path = activity.get_bundle_path()
        os.chdir(bundle_path)
        self.set_title('FlipSticks')
        toolbox = activity.ActivityToolbox(self)
        self.set_toolbox(toolbox)
        toolbox.show()
        if hasattr(self, '_jobject'):
            self._jobject.metadata['title'] = 'FlipSticks'
        title_widget = toolbox._activity_toolbar.title
        title_widget.set_size_request(title_widget.get_layout().get_pixel_size()[0] + 20, -1)

        self.app = flipsticks(self, bundle_path)


        self.set_canvas(self.app)

    def read_file(self, filepath):
        model.load(filepath)
        self.app.restore()
        
    def write_file(self, filepath):
        model.save(filepath)
