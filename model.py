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
import kinematic

class KeyFrame:
    def __init__(self):
        pass

    def empty(self):
        return self.joints == None

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.joints = x.joints.copy()

    def clear(self):
        self.parts = None
        self.sticks = None
        self.scaled_sticks = None
        self.joints = None
        self.scaled_joints = None

class StoredKeyFrame(KeyFrame):
    def __init__(self):
        KeyFrame.__init__(self)
        self.clear()

    def assign(self, x):
        KeyFrame.assign(self, x)
        self.scaled_sticks = x.sticks.copy()
        self.scaled_joints = _initjoints()
        _scalesticks(self.scaled_sticks, .2)
        _setjoints(self.scaled_joints, self.scaled_sticks,
                (self.x, int(theme.KEYFRAMEHEIGHT/2.0)))

class CurrentKeyFrame(KeyFrame):
    def __init__(self):
        KeyFrame.__init__(self)
        self.parts = theme.PARTS.copy()
        self.sticks = theme.STICKS.copy()
        self.joints = _initjoints()
        self.middle = (int(theme.DRAWWIDTH/2.0), int(theme.DRAWHEIGHT/2.0))

    def assign(self, x):
        KeyFrame.assign(self, x)
        _setjoints(self.joints, self.sticks, self.middle)

keys = []

for i in range(5):
    key = StoredKeyFrame()
    keyframe_width = theme.KEYFRAMEWIDTH/5
    key.x = keyframe_width/2 + i*keyframe_width
    keys.append(key)

def _scalesticks(stickdict, i):
    for key in stickdict:
        (angle,len) = stickdict[key]
        newlen = int(len * i)
        stickdict[key] = (angle,newlen)

def _setjoints(joints, sticks, middle):
    # have to traverse in order because
    # parent joints must be set right
    for stickname in theme.STICKLIST:
        (angle,len) = sticks[stickname]
        jname = theme.JOINTS[stickname]
        (x,y) = kinematic.getparentjoint(jname, joints, middle)
        parents = kinematic.getparentsticks(stickname)
        panglesum = 0
        for parentname in parents:
            (pangle,plen) = sticks[parentname]
            panglesum += pangle
        (nx,ny) = kinematic.getpoints(x,y,angle+panglesum,len)
        joints[jname] = (nx,ny)

def _initjoints():
    joints = {}
    for stickname in theme.JOINTS:
        jname = theme.JOINTS[stickname]
        joints[jname] = (0,0)
    return joints
