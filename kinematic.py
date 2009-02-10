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

import model
import theme

class KinematicFrame:
    def __init__(self, keyframe=None):
        if keyframe:
            self.assign(keyframe)
        else:
            self.joints = None
            self.parts = None
            self.middle = None
            self.hsize = None

    def assign(self, keyframe):
        self.joints = keyframe.joints.copy()
        self.parts = keyframe.parts.copy()
        self.middle = keyframe.middle
        self.hsize = keyframe.sticks['HEAD'][1]

def makeframes():
    frames = {}

    for i in model.keys:
        if not i.empty():
            frames[i.x] = KinematicFrame(i)

    if not frames:
        return {}

    fsecs = frames.keys()
    fsecs.sort()

    # set border frames
    frames[0] = frames[fsecs[0]]
    frames[theme.KEYFRAMEWIDTH] = frames[fsecs[-1]]

    # now fill in frames between
    fsecs = frames.keys()
    fsecs.sort()

    # frame interval
    fint = int(theme.KEYFRAMEWIDTH/float(theme.TOTALFRAMES)) 

    for i in range(len(fsecs)):
        if i == len(fsecs)-1:
            continue # nothing after end

        startsecs = fsecs[i]
        endsecs = fsecs[i+1]
        start_frame = frames[startsecs]
        end_frame = frames[endsecs]
        numframes = int((endsecs-startsecs)/float(fint))-1

        for j in range(numframes-1): # MAYBE SHOULD BE numframes
            frame = frames[startsecs + ((j+1)*fint)] = KinematicFrame()

            frame.joints = _intjoints(start_frame.joints, end_frame.joints,
                    j+1, numframes)
            frame.parts = _intparts(start_frame.parts, end_frame.parts,
                    j+1, numframes)
            frame.middle = _intmiddle(start_frame.middle, end_frame.middle,
                    j+1, numframes)
            frame.hsize = _inthsize(start_frame.hsize, end_frame.hsize,
                    j+1, numframes)

    return frames

def _interpolate(x,x0,y0,x1,y1):
    if x1-x0 == 0:
        return y0
    m = float(y1-y0)/float(x1-x0)
    y = y0 + ((x-x0)*m)
    return y

def _intjoints(sjoints, ejoints, count, numpoints):
    # numpoints: number of points between start and end
    # count: point were getting now
    ijoints = {}
    for jname in sjoints:
        (x0,y0) = sjoints[jname]
        (x1,y1) = ejoints[jname]
        #print 'x0:%s,y0:%s' % (x0,y0)
        #print 'x1:%s,y1:%s' % (x1,y1)
        x = x0 + (count * ((x1-x0)/float(numpoints)))
        y = _interpolate(x,x0,y0,x1,y1)
        ijoints[jname] = (int(x),int(y))
    return ijoints

def _intparts(sparts,eparts,count,numpoints):
    iparts = {}
    for pname in sparts:
        x0 = sparts[pname]
        x1 = eparts[pname]
        if x0 == x1:
            iparts[pname] = x0
            continue
        x = x0 + (count * ((x1-x0)/float(numpoints)))
        iparts[pname] = int(x)
    return iparts

def _intmiddle(smiddle,emiddle,count,numpoints):
    (x0,y0) = smiddle
    (x1,y1) = emiddle
    x = x0 + (count * ((x1-x0)/float(numpoints)))
    y = _interpolate(x,x0,y0,x1,y1)
    return (int(x),int(y))

def _inthsize(shsize,ehsize,count,numpoints):
    x0 = shsize
    x1 = ehsize
    if x0 == x1:
        return x0
    x = x0 + (count * ((x1-x0)/float(numpoints)))
    return int(x)
