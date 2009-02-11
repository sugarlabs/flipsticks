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

import theme
import model

class ScreenFrame(model.KeyFrame):
    def __init__(self):
        self.reset()

    def setjoints(self):
        self._setjoints(self.joints, self.sticks, self.middle)

    def reset(self):
        self.parts = theme.PARTS.copy()
        self.sticks = theme.STICKS.copy()
        self.joints = self._initjoints()
        self.middle = (theme.DRAWWIDTH/2, theme.DRAWHEIGHT/3)
        self.setjoints()

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.joints = x.joints.copy()
        self.setjoints()

    def getrotatepoint(self):
        (angle,len) = self.sticks['TORSO']
        x,y = self.middle
        (rx,ry) = self._getpoints(x,y,angle,int(len/2.0))
        return (rx,ry)

    def inrotate(self, x, y):
        rx, ry = self.getrotatepoint()
        if (abs(rx-x) <= 5) and (abs(ry-y) <= 5):
            return True
        return False

    def injoint(self, x, y):
        for jname in self.joints:
            jx, jy = self.joints[jname]
            if (abs(jx-x) <= 5) and (abs(jy-y) <= 5):
                return jname
        return False

    def inmiddle(self, x, y):
        mx, my = self.middle
        if (abs(mx-x) <= 5) and (abs(my-y) <= 5):
            return True
        return False

    def move(self, dx, dy):
        if self.joints:
            for jname in self.joints:
                (jx, jy) = self.joints[jname]
                self.joints[jname] = (jx+dx, jy+dy)
