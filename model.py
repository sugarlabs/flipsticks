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
import pickle

import theme
import kinematic

keys = []

class KeyFrame:
    def __init__(self):
        self.clear()

    def empty(self):
        return self.joints == None

    def assign(self, x):
        self.middle = x.middle
        self.parts = x.parts.copy()
        self.sticks = x.sticks.copy()
        self.joints = x.joints.copy()
        self.scaled_sticks = x.get_scaled_sticks()
        self.scaled_joints = x.get_scaled_joints(self.x,
                int(theme.KEYFRAMEHEIGHT/2.0))

    def clear(self):
        self.middle = None
        self.parts = None
        self.sticks = None
        self.scaled_sticks = None
        self.joints = None
        self.scaled_joints = None

def save(filename):
    out = []

    for i in keys:
        out.append({
            'x'             : i.x,
            'middle'        : i.middle,
            'parts'         : i.parts,
            'sticks'        : i.sticks,
            'joints'        : i.joints,
            'scaled_sticks' : i.scaled_sticks,
            'scaled_joints' : i.scaled_joints })

    file(filename, 'w').write(pickle.dumps(out))

def load(filename):
    inc = pickle.loads(file(filename, 'r').read())

    for i, data in enumerate(inc):
        key = keys[i]

        key.x = data['x']
        key.middle = data['middle']
        key.parts = data['parts']
        key.sticks = data['sticks']
        key.joints = data['joints']
        key.scaled_sticks = data['scaled_sticks']
        key.scaled_joints = data['scaled_joints']

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
    key = KeyFrame()
    keyframe_width = theme.KEYFRAMEWIDTH/5
    key.x = keyframe_width/2 + i*keyframe_width
    keys.append(key)
