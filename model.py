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
import math

try:
    import json
    json.dumps
except (ImportError, AttributeError):
    import simplejson as json

from theme import *

keys = []

class KeyFrame:
    def empty(self):
        return self.joints == None

    def _setjoints(self, joints, sticks, middle):
        if self.empty():
            return

        # have to traverse in order because
        # parent joints must be set right
        for stickname in STICKLIST:
            (angle,len) = sticks[stickname]
            jname = JOINTS[stickname]
            (x,y) = getparentjoint(jname, joints, middle)
            parents = getparentsticks(stickname)
            panglesum = 0
            for parentname in parents:
                (pangle,plen) = sticks[parentname]
                panglesum += pangle
            (nx,ny) = self._getpoints(x,y,angle+panglesum,len)
            joints[jname] = (nx,ny)

    def _getpoints(self, x, y, angle, len):
        nx = int(round(x + (len * math.cos(math.radians(angle)))))
        ny = int(round(y - (len * math.sin(math.radians(angle)))))
        return (nx,ny)

    def _initjoints(self):
        joints = {}
        for stickname in JOINTS:
            jname = JOINTS[stickname]
            joints[jname] = (0,0)
        return joints

class StoredFrame(KeyFrame):
    def __init__(self, data=None):
        if not data:
            self.clear()
        else:
            def array2tuple(a):
                return a and (a[0], a[1])

            def hash2tuple(h):
                if not h:
                    return None
                out = {}
                for i, j in h.items():
                    out[i] = array2tuple(j)
                return out

            self.x = scale_keyframe(data['x'])
            self.middle = scale_middle(data['middle'])
            self.parts = data['parts']
            self.sticks = hash2tuple(data['sticks'])
            self.joints = hash2tuple(data['joints'])
            self._make_thumbs()
            self.setjoints()

    def collect(self):
        return { 'x'             : unscale_keyframe(self.x),
                 'middle'        : unscale_middle(self.middle),
                 'parts'         : self.parts,
                 'sticks'        : self.sticks,
                 'joints'        : self.joints }

    def setjoints(self):
        if not self.empty():
            self._setjoints(self.joints, self.sticks, self.middle)

    def clear(self):
        self.middle = None
        self.parts = None
        self.sticks = None
        self.scaled_sticks = None
        self.joints = None
        self.scaled_joints = None

    def move(self, dx):
        if self.scaled_joints:
            for jname in self.scaled_joints:
                (jx, jy) = self.scaled_joints[jname]
                self.scaled_joints[jname] = (jx+dx, jy)
        self.x += dx

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.joints = x.joints.copy()
        self._make_thumbs()

    def _make_thumbs(self):
        if self.empty():
            self.scaled_sticks = None
            self.scaled_joints = None
            return

        self.scaled_sticks = self.sticks.copy()
        self.scaled_joints = self._initjoints()

        for key in self.scaled_sticks:
            (angle,len) = self.scaled_sticks[key]
            newlen = int(len * .2)
            self.scaled_sticks[key] = (angle,newlen)

        self._setjoints(self.scaled_joints, self.scaled_sticks,
                (self.x, KEYFRAMEHEIGHT/2))

def save(filename):
    out = []

    for i in keys:
        out.append(i.collect())

    file(filename, 'w').write(json.dumps(out))

def load(filename):
    inc = json.loads(file(filename, 'r').read())

    for i, data in enumerate(inc):
        keys[i] = StoredFrame(data)

def getparentsticks(stickname):
    if stickname in ['RIGHT SHOULDER','LEFT SHOULDER','NECK','TORSO']:
        return []
    if stickname in ['HEAD']:
        return ['NECK']
    if stickname == 'UPPER RIGHT ARM':
        return ['RIGHT SHOULDER']
    if stickname == 'LOWER RIGHT ARM':
        return ['UPPER RIGHT ARM','RIGHT SHOULDER']
    if stickname == 'UPPER LEFT ARM':
        return ['LEFT SHOULDER']
    if stickname == 'LOWER LEFT ARM':
        return ['UPPER LEFT ARM','LEFT SHOULDER']
    if stickname == 'RIGHT HIP':
        return ['TORSO']
    if stickname == 'UPPER RIGHT LEG':
        return ['RIGHT HIP','TORSO']
    if stickname == 'LOWER RIGHT LEG':
        return ['UPPER RIGHT LEG','RIGHT HIP','TORSO']
    if stickname == 'RIGHT FOOT':
        return ['LOWER RIGHT LEG','UPPER RIGHT LEG','RIGHT HIP','TORSO']
    if stickname == 'LEFT HIP':
        return ['TORSO']
    if stickname == 'UPPER LEFT LEG':
        return ['LEFT HIP','TORSO']
    if stickname == 'LOWER LEFT LEG':
        return ['UPPER LEFT LEG','LEFT HIP','TORSO']
    if stickname == 'LEFT FOOT':
        return ['LOWER LEFT LEG','UPPER LEFT LEG','LEFT HIP','TORSO']

def getparentjoint(jname, joints, middle):
    if jname in ['rightshoulder','leftshoulder','groin','neck']:
        return middle

    parentjoints = {'rightelbow':'rightshoulder',
                    'righthand':'rightelbow',
                    'leftelbow':'leftshoulder',
                    'lefthand':'leftelbow',
                    'righthip':'groin',
                    'rightknee':'righthip',
                    'rightheel':'rightknee',
                    'righttoe':'rightheel',
                    'lefthip':'groin',
                    'leftknee':'lefthip',
                    'leftheel':'leftknee',
                    'lefttoe':'leftheel',
                    'head':'neck'}

    return joints[parentjoints[jname]]

def screen_shot(pixbuf):
    tmpdir = '/tmp'

    filename = 'fp%03d.png' % i
    filepath = os.path.join(tmpdir,filename)
    pixbuf.save(filepath,'png')

    from sugar.datastore import datastore
    mediaObject = datastore.create()
    mediaObject.metadata['title'] = 'FlipSticks PNG'
    thumbData = _get_base64_pixbuf_data(pixbuf)
    mediaObject.metadata['preview'] = thumbData
    #medaiObject.metadata['icon-color'] = ''
    mediaObject.metadata['mime_type'] = 'image/png'
    mediaObject.file_path = filepath
    datastore.write(mediaObject)

def _save_data_to_buffer_cb(buf, data):
    data[0] += buf
    return True

def _get_base64_pixbuf_data(pixbuf):
    data = [""]
    pixbuf.save_to_callback(_save_data_to_buffer_cb, "png", {}, data)
    import base64
    return base64.b64encode(str(data[0]))

for i in range(5):
    key = StoredFrame()
    keyframe_width = KEYFRAMEWIDTH/5
    key.x = keyframe_width/2 + i*keyframe_width
    keys.append(key)
