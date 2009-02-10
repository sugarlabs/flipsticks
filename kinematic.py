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

import model
import theme

class Frame:
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
            frames[i.x] = Frame(i)

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
            frame = frames[startsecs + ((j+1)*fint)] = Frame()

            frame.joints = _intjoints(start_frame.joints, end_frame.joints,
                    j+1, numframes)
            frame.parts = _intparts(start_frame.parts, end_frame.parts,
                    j+1, numframes)
            frame.middle = _intmiddle(start_frame.middle, end_frame.middle,
                    j+1, numframes)
            frame.hsize = _inthsize(start_frame.hsize, end_frame.hsize,
                    j+1, numframes)

    return frames

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

def getpoints(x,y,angle,len):
    nx = int(round(x + (len * math.cos(math.radians(angle)))))
    ny = int(round(y - (len * math.sin(math.radians(angle)))))
    return (nx,ny)

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


"""
    def makeframes(self):
        endsecs = KEYFRAMEWIDTH
        fint = int(endsecs/float(TOTALFRAMES)) # frame interval
        self.frames = {}
        self.fparts = {}
        self.fmiddles = {}
        self.fhsize = {}
        for i in range(len(self.keyframes)):
            secs = self.keyframes[i]
            if model.keys[i].joints:
                self.frames[secs] = model.keys[i].joints.copy()
                self.fparts[secs] = model.keys[i].parts.copy()
                self.fmiddles[secs] = model.keys[i].middle
                #print '%s:KFMIDDLE:%s = (%s,%s)' % (i,secs,self.fmiddles[secs][0],self.fmiddles[secs][1])
                self.fhsize[secs] = model.keys[i].sticks['HEAD'][1]
        fsecs = self.frames.keys()
        fsecs.sort()
        if not fsecs:
            return
        # ADD frame at 0
        self.frames[0] = self.frames[fsecs[0]].copy()
        self.fparts[0] = self.fparts[fsecs[0]].copy()
        self.fmiddles[0] = self.fmiddles[fsecs[0]]
        self.fhsize[0] = self.fhsize[fsecs[0]]
        # ADD frame at end
        self.frames[endsecs] = self.frames[fsecs[-1]].copy()
        self.fparts[endsecs] = self.fparts[fsecs[-1]].copy()
        self.fmiddles[endsecs] = self.fmiddles[fsecs[-1]]
        self.fhsize[endsecs] = self.fhsize[fsecs[-1]]
        # now fill in frames between
        fsecs = self.frames.keys()
        fsecs.sort()
        for i in range(len(fsecs)):
            if i == len(fsecs)-1:
               continue # nothing after end
            startsecs = fsecs[i]
            endsecs = fsecs[i+1]
            numframes = int((endsecs-startsecs)/float(fint))-1
            #print 'NUMFRAMES(%s):%s' % (i,numframes)
            for j in range(numframes-1): # MAYBE SHOULD BE numframes
                secs = startsecs + ((j+1)*fint)
                self.frames[secs] = self.intjoints(self.frames[startsecs],self.frames[endsecs],
                                                   j+1,numframes)
                self.fparts[secs] = self.intparts(self.fparts[startsecs],self.fparts[endsecs],
                                                  j+1,numframes)
                self.fmiddles[secs] = self.intmiddle(self.fmiddles[startsecs],self.fmiddles[endsecs],
                                                     j+1,numframes)
                self.fhsize[secs] = self.inthsize(self.fhsize[startsecs],self.fhsize[endsecs],
                                                  j+1,numframes)
                #print '%s,%s(%s secs):(%s,%s) START(%s,%s) - END(%s,%s) startsecs:%s endsecs:%s numframes:%s' % (i,j,secs,self.fmiddles[secs][0],self.fmiddles[secs][1],self.fmiddles[startsecs][0],self.fmiddles[startsecs][1],self.fmiddles[endsecs][0],self.fmiddles[endsecs][1],startsecs,endsecs,numframes)
        #print self.frames.keys()

"""
