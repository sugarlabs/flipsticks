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
        self.clear()

    def empty(self):
        return self.joints == None

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.scaled_sticks = x.sticks.copy()
        self.joints = x.joints.copy()
        self.scaled_joints = initjoints()

        scalesticks(self.scaled_sticks, .2)
        setjoints(self.scaled_joints, self.scaled_sticks,
                (self.x, int(theme.KEYFRAMEHEIGHT/2.0)))

    def clear(self):
        self.parts = None
        self.sticks = None
        self.scaled_sticks = None
        self.joints = None
        self.scaled_joints = None

keys = []

for i in range(5):
    key = KeyFrame()
    keyframe_width = theme.KEYFRAMEWIDTH/5
    key.x = keyframe_width/2 + i*keyframe_width
    keys.append(key)

def initjoints():
    joints = {}
    for stickname in theme.JOINTS:
        jname = theme.JOINTS[stickname]
        joints[jname] = (0,0)
    return joints

def scalesticks(stickdict, i):
    for key in stickdict:
        (angle,len) = stickdict[key]
        newlen = int(len * i)
        stickdict[key] = (angle,newlen)

def setjoints(joints, sticks, middle):
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
