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

import math

import theme
import model

class ScreenFrame:
    def __init__(self):
        self.reset()

    def setjoints(self):
        _setjoints(self.joints, self.sticks, self.middle)

    def reset(self):
        self.parts = theme.PARTS.copy()
        self.sticks = theme.STICKS.copy()
        self.joints = _initjoints()
        self.middle = (int(theme.DRAWWIDTH/2.0), int(theme.DRAWHEIGHT/2.0))
        self.setjoints()

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.joints = x.joints.copy()
        self.setjoints()

    def get_scaled_sticks(self):
        out = self.sticks.copy()
        for key in out:
            (angle,len) = out[key]
            newlen = int(len * .2)
            out[key] = (angle,newlen)
        return out

    def get_scaled_joints(self, x, y):
        out = _initjoints()
        _setjoints(out, self.get_scaled_sticks(), (x, y))
        return out

    def getrotatepoint(self):
        (angle,len) = self.sticks['TORSO']
        x,y = self.middle
        (rx,ry) = _getpoints(x,y,angle,int(len/2.0))
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

def _initjoints():
    joints = {}
    for stickname in theme.JOINTS:
        jname = theme.JOINTS[stickname]
        joints[jname] = (0,0)
    return joints

def _setjoints(joints, sticks, middle):
    # have to traverse in order because
    # parent joints must be set right
    for stickname in theme.STICKLIST:
        (angle,len) = sticks[stickname]
        jname = theme.JOINTS[stickname]
        (x,y) = model.getparentjoint(jname, joints, middle)
        parents = model.getparentsticks(stickname)
        panglesum = 0
        for parentname in parents:
            (pangle,plen) = sticks[parentname]
            panglesum += pangle
        (nx,ny) = _getpoints(x,y,angle+panglesum,len)
        joints[jname] = (nx,ny)

def _getpoints(x,y,angle,len):
    nx = int(round(x + (len * math.cos(math.radians(angle)))))
    ny = int(round(y - (len * math.sin(math.radians(angle)))))
    return (nx,ny)
