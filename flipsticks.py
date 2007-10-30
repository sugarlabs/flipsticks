#!/usr/bin/env python

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
#


### flipsticks
###
### author: Ed Stoner (ed@whsd.net)
### (c) 2007 World Wide Workshop Foundation

import time
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import os
import math
import textwrap
import pickle

SERVICE = 'org.freedesktop.Telepathy.Tube.Connect'
IFACE = SERVICE
PATH = '/org/freedesktop/Telepathy/Tube/Connect'
GRAY = "#B7B7B7" # gray
PINK = "#FF0099" # pink
YELLOW = "#FFFF00" # yellow
WHITE = "#FFFFFF"
BLACK = "#000000"
BACKGROUND = "#66CC00" # light green
BUTTON_FOREGROUND = "#CCFB99" # very light green
BUTTON_BACKGROUND = "#027F01" # dark green
COLOR_FG_BUTTONS = (
    (gtk.STATE_NORMAL,"#CCFF99"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#CCFF99"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#CCFF99"),
    ) # very light green
COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )
OLD_COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#014D01"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#027F01"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )

SPANISH = u'Espa\xf1ol'
LANG = {'English':{'size':'Size',
                   'angle':'Angle',
		   'lessonplan':'Lesson Plans',
		   'lpdir':'lp-en',
		   'export':'Export Frame One',
		   'HEAD':'Head',
		   'NECK':'Neck',
		   'RIGHT SHOULDER':'Right Shoulder',
		   'UPPER RIGHT ARM':'Upper Right Arm',
		   'LOWER RIGHT ARM':'Lower Right Arm',
		   'RIGHT HAND':'Right Hand',
		   'LEFT SHOULDER':'Left Shoulder',
		   'UPPER LEFT ARM':'Upper Left Arm',
		   'LOWER LEFT ARM':'Lower Left Arm',
		   'LEFT HAND':'Left Hand',
		   'TORSO':'Torso',
		   'RIGHT HIP':'Right Hip',
		   'UPPER RIGHT LEG':'Upper Right Leg',
		   'LOWER RIGHT LEG':'Lower Right Leg',
		   'RIGHT FOOT':'Right Foot',
		   'LEFT HIP':'Left Hip',
		   'UPPER LEFT LEG':'Upper Left Leg',
		   'LOWER LEFT LEG':'Lower Left Leg',
		   'LEFT FOOT':'Left Foot'},
	SPANISH:{'size':u'Tama\xf1o',
	         'angle':u'\xe1ngulo',
		 'lessonplan':u'Planes de la lecci\xf3n',
		 'lpdir':'lp-en',
		 'export':'Un marco de la exportacion',
		 'HEAD':'Cabeza',
		 'NECK':'Cuello',
		 'RIGHT SHOULDER':'Hombro derecho',
		 'UPPER RIGHT ARM':'Brazo derecho superior',
		 'LOWER RIGHT ARM':'Bajar el brazo derecho',
		 'RIGHT HAND':'Mano derecha',
		 'LEFT SHOULDER':'Hombro izquierdo',
		 'UPPER LEFT ARM':'Brazo izquierdo superior',
		 'LOWER LEFT ARM':u'Un brazo izquierdo m\xe1s bajo',
		 'LEFT HAND':'Mano izquierda',
		 'TORSO':'Torso',
		 'RIGHT HIP':'Cadera derecha',
		 'UPPER RIGHT LEG':'Pierna derecha superior',
		 'LOWER RIGHT LEG':'Bajar la pierna derecha',
		 'RIGHT FOOT':'Pie derecho',
		 'LEFT HIP':'Cadera izquierda',
		 'UPPER LEFT LEG':'Pierna izquierda superior',
		 'LOWER LEFT LEG':u'Una pierna izquierda m\xe1s baja',
		 'LEFT FOOT':'Pie izquierdo'}}

DRAWWIDTH = 750
DRAWHEIGHT = 500
FPWIDTH = 150
FPHEIGHT = 100
#DRAWHEIGHT = 300 for my laptop
KEYFRAMEWIDTH = 675
KEYFRAMEHEIGHT = 80

KEYFRAMES = [50,190,337,487,625]
TOTALFRAMES = 30

STICKS = {'HEAD':(0,15),
          'NECK':(90,15),
	  'RIGHT SHOULDER':(185,25),
	  'UPPER RIGHT ARM':(60,35),
	  'LOWER RIGHT ARM':(35,35),
	  'LEFT SHOULDER':(355,25),
	  'UPPER LEFT ARM':(300,35),
	  'LOWER LEFT ARM':(325,35),
	  'TORSO':(270,60),
	  'RIGHT HIP':(80,20),
	  'UPPER RIGHT LEG':(300,50),
	  'LOWER RIGHT LEG':(340,40),
	  'RIGHT FOOT':(85,15),
	  'LEFT HIP':(280,20),
	  'UPPER LEFT LEG':(65,50),
	  'LOWER LEFT LEG':(15,40),
	  'LEFT FOOT':(275,15)}

PARTS = {'RIGHT HAND':14,
	 'LEFT HAND':14}


STICKLIST = ['NECK','HEAD','RIGHT SHOULDER','UPPER RIGHT ARM','LOWER RIGHT ARM',
             'LEFT SHOULDER','UPPER LEFT ARM','LOWER LEFT ARM','TORSO',
	     'RIGHT HIP','UPPER RIGHT LEG','LOWER RIGHT LEG','RIGHT FOOT',
	     'LEFT HIP','UPPER LEFT LEG','LOWER LEFT LEG','LEFT FOOT']

LABELLIST = ['HEAD','NECK','RIGHT SHOULDER','UPPER RIGHT ARM','LOWER RIGHT ARM',
             'RIGHT HAND','LEFT SHOULDER','UPPER LEFT ARM','LOWER LEFT ARM','LEFT HAND',
	     'TORSO','RIGHT HIP','UPPER RIGHT LEG','LOWER RIGHT LEG','RIGHT FOOT',
	     'LEFT HIP','UPPER LEFT LEG','LOWER LEFT LEG','LEFT FOOT']

# The joint is the circle at the end of the stick

JOINTS = {'HEAD':'head',
          'NECK':'neck',
	  'RIGHT SHOULDER':'rightshoulder',
	  'UPPER RIGHT ARM':'rightelbow',
	  'LOWER RIGHT ARM':'righthand',
	  'LEFT SHOULDER':'leftshoulder',
	  'UPPER LEFT ARM':'leftelbow',
	  'LOWER LEFT ARM':'lefthand',
	  'TORSO':'groin',
	  'RIGHT HIP':'righthip',
	  'UPPER RIGHT LEG':'rightknee',
	  'LOWER RIGHT LEG':'rightheel',
	  'RIGHT FOOT':'righttoe',
	  'LEFT HIP':'lefthip',
	  'UPPER LEFT LEG':'leftknee',
	  'LOWER LEFT LEG':'leftheel',
	  'LEFT FOOT':'lefttoe'}

JOINTTOSTICK = {}
for jname in JOINTS:
    JOINTTOSTICK[JOINTS[jname]] = jname

PARTS = {'HEAD':40,
         'RIGHT HAND':14,
	 'LEFT HAND':14}

TESTSTICKS = {'RIGHT SHOULDER':(37,20),
              'UPPER RIGHT ARM':(6,15),
	      'LOWER RIGHT ARM':(10,15)}

def getwrappedfile(filepath,linelength):
    text = []
    f = file(filepath)
    for line in f:
        if line == '\n':
	    text.append(line)
	else:
            for wline in textwrap.wrap(line.strip()):
	        text.append('%s\n' % wline)
    return ''.join(text)

def capwords(s):
    x = s.split()
    n = []
    for word in x:
        n.append(word.capitalize())
    return ' '.join(n)

def prepare_btn(btn, w=-1, h=-1):
    for state, color in COLOR_BG_BUTTONS:
        btn.modify_bg(state, gtk.gdk.color_parse(color))
    c = btn.get_child()
    if c is not None:
        for state, color in COLOR_FG_BUTTONS:
            c.modify_fg(state, gtk.gdk.color_parse(color))
    else:
        for state, color in COLOR_FG_BUTTONS:
            btn.modify_fg(state, gtk.gdk.color_parse(color))
    if w>0 or h>0:
        btn.set_size_request(w, h)
    return btn

def inarea(x,y,awidth,aheight):
    if x+5 > awidth:
        return False
    if y+5 > aheight:
        return False
    if y < 5:
        return False
    if x < 5:
        return False
    return True

def interpolate(x,x0,y0,x1,y1):
    if x1-x0 == 0:
        return y0
    m = float(y1-y0)/float(x1-x0)
    y = y0 + ((x-x0)*m)
    return y

def getpoints(x,y,angle,len):
    nx = int(round(x + (len * math.cos(math.radians(angle)))))
    ny = int(round(y - (len * math.sin(math.radians(angle)))))
    return (nx,ny)

def scalesticks(stickdict,i):
    for key in stickdict:
        (angle,len) = stickdict[key]
	newlen = int(len * i)
	stickdict[key] = (angle,newlen)

class flipsticks:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def expose_event(self, widget, event):
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.pixmap, x, y, x, y, width, height)
        return False

    def kf_expose_event(self, widget, event):
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.kfpixmap, x, y, x, y, width, height)
        return False

    def fp_expose_event(self, widget, event):
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.fppixmap, x, y, x, y, width, height)
        return False

    def configure_event(self, widget, event):
        x, y, width, height = self.mfdraw.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
	self.drawmainframe()
        return True

    def kf_configure_event(self, widget, event):
        self.drawkeyframe()
	return True

    def fp_configure_event(self, widget, event):
	self.drawfp()
        return True

    def motion_notify_event(self, widget, event):
        if event.is_hint:
	    x, y, state = event.window.get_pointer()
	else:
	    x = event.x
	    y = event.y
	    state = event.state
	if state & gtk.gdk.BUTTON1_MASK and self.pixmap != None:
	    if self.jointpressed:
	        if inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
	            #self.joints[self.jointpressed] = (x,y) # old hack way
		    # first find the parents x,y
		    (px,py) = self.getparentjoint(self.jointpressed,self.joints,
		                                  self.middle)
		    if x-px == 0:
			#computeangle = 0
			b = 1
		    else:
			b = float(px-x)
		    a = float(y-py)
		    computeangle = int(math.degrees(math.atan(a/b)))
		    stickname = JOINTTOSTICK[self.jointpressed]
		    # add sum of parent angles to new angle
	            parents = self.getparentsticks(stickname)
	            panglesum = 0
	            for parentname in parents:
	                (pangle,plen) = self.sticks[parentname]
		        panglesum += pangle
	            (angle, len) = self.sticks[stickname]
		    #print 'X:%s,Y:%s,PX:%s,PY:%s,ANGLE:%s,NEWANGLE:%s' % (x,y,px,py,angle,newangle)
		    newangle = computeangle-panglesum
		    if (x < px) or (b == 1):
		        newangle = newangle + 180
		    if newangle < 0:
		        newangle = 360 + newangle
	            self.sticks[stickname] = (newangle,len)
                    self.setjoints() # this is overkill
		    self.drawmainframe()
		    self.updateentrybox()
	    elif self.middlepressed:
	        if inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
		    xdiff = x-self.middle[0]
		    ydiff = y-self.middle[1]
		    self.shiftjoints(xdiff,ydiff)
	            self.middle = (x,y)
		    self.drawmainframe()
	    elif self.rotatepressed:
	        if inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
		    (px,py) = self.middle
		    if x-px == 0:
			#computeangle = 0
			b = 1
		    else:
			b = float(px-x)
		    a = float(y-py)
		    computeangle = int(math.degrees(math.atan(a/b)))
		    stickname = 'TORSO'
	            (angle, len) = self.sticks[stickname]
		    newangle = computeangle
		    if (x < px) or (b == 1):
		        newangle = newangle + 180
		    if newangle < 0:
		        newangle = 360 + newangle
		    anglediff = newangle-angle
		    self.sticks[stickname] = (newangle,len)
		    # now rotate the other sticks off of the middle
		    for stickname in ['NECK','RIGHT SHOULDER','LEFT SHOULDER']:
		        (sangle,slen) = self.sticks[stickname]
		        newsangle = sangle+anglediff
		        if newsangle < 0:
		            newsangle = 360 + newsangle
			if newsangle > 360:
			    newsangle = newsangle - 360
		        self.sticks[stickname] = (newsangle,slen)
		    self.setjoints()
		    self.drawmainframe()
		    self.updateentrybox()
		    
	return True

    def kf_motion_notify_event(self, widget, event):
        if event.is_hint:
	    x, y, state = event.window.get_pointer()
	else:
	    x = event.x
	    y = event.y
	    state = event.state
	if state & gtk.gdk.BUTTON1_MASK and self.pixmap != None:
	    if self.kfpressed >= 0:
	        if inarea(x,y,KEYFRAMEWIDTH,KEYFRAMEHEIGHT):
		    xdiff = x-self.keyframes[self.kfpressed]
		    self.shiftjoints(xdiff,0,self.kfsjoints[self.kfpressed])
	            self.keyframes[self.kfpressed] = x
		    self.drawkeyframe()
	return True

    def button_press_event(self, widget, event):
        if event.button == 1 and self.pixmap != None:
	    joint = self.injoint(event.x, event.y)
	    if joint:
	        self.jointpressed = joint
		self.drawmainframe()
	    elif self.inmiddle(event.x, event.y):
	        self.middlepressed = True
		self.drawmainframe()
	    elif self.inrotate(event.x, event.y):
	        self.rotatepressed = True
		self.drawmainframe()
	return True

    def syncmaintokf(self):
	# set the main window to the keyframe
        if self.kfsticks[self.kfselected]:
            self.sticks = self.kfsticks[self.kfselected].copy()
            self.parts = self.kfparts[self.kfselected].copy()
            self.middle = self.kfmiddles[self.kfselected]
            self.setjoints()
            self.drawmainframe()

    def kf_button_press_event(self, widget, event):
        if event.button == 1 and self.pixmap != None:
	    kfnum = self.inkeyframe(event.x, event.y)
	    if kfnum >= 0:
	        self.kfpressed = kfnum
		self.kfselected = kfnum
		self.drawkeyframe()
		self.syncmaintokf()
	        self.updateentrybox()
	return True

    def button_release_event(self, widget, event):
        self.jointpressed = None
	self.middlepressed = False
	self.rotatepressed = False
	self.drawmainframe()
	return True

    def kf_button_release_event(self, widget, event):
        self.kfpressed = -1
	self.drawkeyframe()
        return True

    def setplayspeed(self,adj):
	#self.waittime = int((6-adj.value)*150)
	self.waittime = int((6-adj.value)*75)
	if self.playing:
	    gobject.source_remove(self.playing)
	    self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def playframe(self):
	if not self.playing:
	    return False
	else:
	    if self.playframenum == -1:
	        return True
        joints = self.frames[self.playframenum]
	parts = self.fparts[self.playframenum]
	# draw on the main drawing area
        area = self.toplevel.window
	drawgc = area.new_gc()
	drawgc.line_width = 3
	cm = drawgc.get_colormap()
	white = cm.alloc_color('white')
	black = cm.alloc_color('black')
	drawgc.fill = gtk.gdk.SOLID
        x, y, width, height = self.mfdraw.get_allocation()
        #self.pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
	# clear area
	drawgc.set_foreground(white)
        self.pixmap.draw_rectangle(drawgc,True,0,0,width,height)

	drawgc.set_foreground(black)
	#hsize = self.sticks['HEAD'][1] # really half of head size
	hsize = self.fhsize[self.playframenum]
	middle = self.fmiddles[self.playframenum]
	rhsize = parts['RIGHT HAND']
	lhsize = parts['LEFT HAND']
	self.drawstickman(drawgc,self.pixmap,middle,joints,hsize,rhsize,lhsize)
	# draw circle for middle
	#green = cm.alloc_color('green')
	#drawgc.set_foreground(green)
	#x,y = middle
	#self.pixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
	self.mfdraw.queue_draw()

	fsecs = self.frames.keys()
	fsecs.sort()
        if self.playingbackwards:
	    # decrement playframenum
	    if self.playframenum == fsecs[0]:
	        self.playframenum = fsecs[-1]
            else:
	        i = fsecs.index(self.playframenum)
		self.playframenum = fsecs[i-1]
	else:
            # increment playframenum
	    if self.playframenum == fsecs[-1]:
	        self.playframenum = fsecs[0]
	    else:
	        i = fsecs.index(self.playframenum)
	        self.playframenum = fsecs[i+1]
        if self.playing:
	    return True
	else:
	    return False

    def enterangle_callback(self, widget, entry):
        stickname = self.stickselected
	if stickname in self.sticks:
            newangle = int(entry.get_text())
	    (angle, len) = self.sticks[stickname]
	    self.sticks[stickname] = (newangle,len)
	else:
	    # part not stick
	    self.angleentry.set_text('-')
	self.setjoints()
	self.drawmainframe()

    def updateentrybox(self):
	if self.stickselected in self.sticks:
            (angle, len) = self.sticks[self.stickselected]
            self.angleentry.set_text(str(angle))
	else:
	    # part not stick
	    len = self.parts[self.stickselected]
	self.sizeentry.set_text(str(len))

    def enterlen_callback(self, widget, entry):
        stickname = self.stickselected
        newlen = int(entry.get_text())
	if stickname in self.sticks:
	    if stickname == 'HEAD':
	        newlen = int(newlen/2.0)
	    (angle, len) = self.sticks[stickname]
	    self.sticks[stickname] = (angle,newlen)
	else:
	    # part not stick
	    self.parts[stickname] = newlen
	self.setjoints()
	self.drawmainframe()

    def reset(self, widget, data=None):
	xmiddle = int(DRAWWIDTH/2.0)
	ymiddle = int(DRAWHEIGHT/2.0)
	self.middle = (xmiddle,ymiddle)
	self.sticks = STICKS.copy()
	self.parts = PARTS.copy()
	self.selectstickebox()
	self.setjoints()
        self.drawmainframe()

    def setframe(self, widget, data=None):
        self.kfmiddles[self.kfselected] = self.middle
	self.kfparts[self.kfselected] = self.parts.copy()
        self.kfsticks[self.kfselected] = self.sticks.copy()
        self.kfssticks[self.kfselected] = self.sticks.copy()
	scalesticks(self.kfssticks[self.kfselected],.2)
	self.kfjoints[self.kfselected] = self.joints.copy()
	self.kfsjoints[self.kfselected] = self.initjoints()
        #x, y, width, height = self.kfdraw.get_allocation()
	#y = int(height/2.0)
	#y = int(KEYFRAMEHEIGHT/2.0)-5
	y = int(KEYFRAMEHEIGHT/2.0)
	x = self.keyframes[self.kfselected]
	kfmiddle = (x,y)
	self.setjoints(self.kfsjoints[self.kfselected],self.kfssticks[self.kfselected],kfmiddle)
	self.drawkeyframe()

    def clearframe(self, widget, data=None):
        self.kfsticks[self.kfselected] = None
        self.kfssticks[self.kfselected] = None
	self.kfjoints[self.kfselected] = None
	self.kfsjoints[self.kfselected] = None
	self.kfparts[self.kfselected] = None
	self.drawkeyframe()

    def intjoints(self,sjoints,ejoints,count,numpoints):
        # numpoints: number of points between start and end
	# count: point were getting now
	ijoints = {}
	for jname in sjoints:
	    (x0,y0) = sjoints[jname]
	    (x1,y1) = ejoints[jname]
	    #print 'x0:%s,y0:%s' % (x0,y0)
	    #print 'x1:%s,y1:%s' % (x1,y1)
	    x = x0 + (count * ((x1-x0)/float(numpoints)))
	    y = interpolate(x,x0,y0,x1,y1)
	    ijoints[jname] = (int(x),int(y))
	return ijoints

    def intparts(self,sparts,eparts,count,numpoints):
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

    def inthsize(self,shsize,ehsize,count,numpoints):
	x0 = shsize
	x1 = ehsize
	if x0 == x1:
	    return x0
	x = x0 + (count * ((x1-x0)/float(numpoints)))
        return int(x)

    def intmiddle(self,smiddle,emiddle,count,numpoints):
        (x0,y0) = smiddle
	(x1,y1) = emiddle
	x = x0 + (count * ((x1-x0)/float(numpoints)))
	y = interpolate(x,x0,y0,x1,y1)
	return (int(x),int(y))

    def makeframes(self):
	endsecs = KEYFRAMEWIDTH
	fint = int(endsecs/float(TOTALFRAMES)) # frame interval
        self.frames = {}
	self.fparts = {}
	self.fmiddles = {}
	self.fhsize = {}
	kf = {} # point to keyframes by x-middle (which represents a time, like seconds)
	for i in range(len(self.keyframes)):
	    secs = self.keyframes[i]
	    #kf[secs] = i
	    # use self.kfjoints[kf[secs]] and self.kfparts[kf[secs]]
	    if self.kfjoints[i]:
	        self.frames[secs] = self.kfjoints[i].copy()
	        self.fparts[secs] = self.kfparts[i].copy()
	        self.fmiddles[secs] = self.kfmiddles[i]
	        #print '%s:KFMIDDLE:%s = (%s,%s)' % (i,secs,self.fmiddles[secs][0],self.fmiddles[secs][1])
	        self.fhsize[secs] = self.kfsticks[i]['HEAD'][1]
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

    def shiftjoints(self,xdiff,ydiff,joints=None):
        if not joints:
	    joints = self.joints
        for jname in joints:
	    #if isinstance(self.joints[jname],tuple):
	    (jx,jy) = joints[jname]
	    njx = jx + xdiff
	    njy = jy + ydiff
	    joints[jname] = (njx,njy)

    def initjoints(self):
        joints = {}
        for stickname in JOINTS:
	    jname = JOINTS[stickname]
	    joints[jname] = (0,0)
	return joints

    def getparentsticks(self, stickname):
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

    def getparentjoint(self,jname,joints,middle):
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

    def setjoints(self,joints=None,sticks=None,middle=None):
        if not joints:
	    joints = self.joints
	if not sticks:
	    sticks = self.sticks
	if not middle:
	    middle = self.middle
        # have to traverse in order because
	# parent joints must be set right
	for stickname in self.sticklist:
	    (angle,len) = sticks[stickname]
	    jname = JOINTS[stickname]
	    (x,y) = self.getparentjoint(jname,joints,middle)
	    parents = self.getparentsticks(stickname)
	    panglesum = 0
	    for parentname in parents:
	        (pangle,plen) = sticks[parentname]
		panglesum += pangle
	    (nx,ny) = getpoints(x,y,angle+panglesum,len)
	    joints[jname] = (nx,ny)

    def drawmainframe(self):
        area = self.toplevel.window
	drawgc = area.new_gc()
	drawgc.line_width = 3
	cm = drawgc.get_colormap()
	red = cm.alloc_color('red')
	yellow = cm.alloc_color('yellow')
	white = cm.alloc_color('white')
	black = cm.alloc_color('black')
	blue = cm.alloc_color('blue')
	green = cm.alloc_color('green')
	drawgc.fill = gtk.gdk.SOLID
        x, y, width, height = self.mfdraw.get_allocation()
        #self.pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
	# clear area
	drawgc.set_foreground(white)
        self.pixmap.draw_rectangle(drawgc,True,0,0,width,height)

	drawgc.set_foreground(black)
	hsize = self.sticks['HEAD'][1] # really half of head size
	rhsize = self.parts['RIGHT HAND']
	lhsize = self.parts['LEFT HAND']
	self.drawstickman(drawgc,self.pixmap,self.middle,self.joints,hsize,rhsize,lhsize)
	# draw circle for middle
	drawgc.set_foreground(green)
	if self.middlepressed:
	    drawgc.set_foreground(blue)
	x,y = self.middle
	self.pixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
	# draw circle for rotate (should be halfway between middle and groin
	(rx,ry) = self.getrotatepoint()
	drawgc.set_foreground(yellow)
	if self.rotatepressed:
	    drawgc.set_foreground(blue)
	self.pixmap.draw_arc(drawgc,True,rx-5,ry-5,10,10,0,360*64)
	# draw circles for joints
	drawgc.set_foreground(black)
	for jname in self.joints:
	    if jname == 'head':
	       continue
	    x,y = self.joints[jname]
	    if self.jointpressed == jname:
	        drawgc.set_foreground(blue)
	        self.pixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
		drawgc.set_foreground(black)
	    else:
	        drawgc.set_foreground(red)
	        self.pixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
	        drawgc.set_foreground(black)
	self.mfdraw.queue_draw()

    def drawstickman(self,drawgc,pixmap,middle,joints,hsize,rhsize,lhsize):
	leftarm = [middle, joints['leftshoulder'],joints['leftelbow'],joints['lefthand']]
	rightarm = [middle, joints['rightshoulder'],joints['rightelbow'],joints['righthand']]
	torso = [joints['neck'],middle,joints['groin']]
	leftleg = [joints['groin'],joints['lefthip'],joints['leftknee'],
	           joints['leftheel'],joints['lefttoe']]
	rightleg = [joints['groin'],joints['righthip'],joints['rightknee'],
	            joints['rightheel'],joints['righttoe']]
	# draw lines
	pixmap.draw_lines(drawgc, leftarm)
	pixmap.draw_lines(drawgc, rightarm)
	pixmap.draw_lines(drawgc, torso)
	pixmap.draw_lines(drawgc, leftleg)
	pixmap.draw_lines(drawgc, rightleg)
	# draw head
	x,y = joints['head']
	pixmap.draw_arc(drawgc,True,x-hsize,y-hsize,hsize*2,hsize*2,0,360*64)
	# draw circles for hands
	x,y = joints['righthand']
	pixmap.draw_arc(drawgc,True,x-int(rhsize/2.0),y-int(rhsize/2.0),rhsize,rhsize,0,360*64)
	x,y = joints['lefthand']
	pixmap.draw_arc(drawgc,True,x-int(lhsize/2.0),y-int(lhsize/2.0),lhsize,lhsize,0,360*64)
	
    def drawkeyframe(self):
        area = self.toplevel.window
	drawgc = area.new_gc()
	drawgc.line_width = 2
	cm = drawgc.get_colormap()
	red = cm.alloc_color('red')
	white = cm.alloc_color('white')
	black = cm.alloc_color('black')
	blue = cm.alloc_color('blue')
	green = cm.alloc_color('green')
	pink = cm.alloc_color(PINK)
	bgcolor = cm.alloc_color(BACKGROUND)
	darkgreen = cm.alloc_color(BUTTON_BACKGROUND)
	drawgc.fill = gtk.gdk.SOLID
        x, y, width, height = self.kfdraw.get_allocation()
        self.kfpixmap = gtk.gdk.Pixmap(self.kfdraw.window, width, height)
	# clear area
	drawgc.set_foreground(bgcolor)
        self.kfpixmap.draw_rectangle(drawgc,True,0,0,width,height)
	# draw line in middle
	drawgc.set_foreground(darkgreen)
	self.kfpixmap.draw_rectangle(drawgc,True,10,int(height/2.0)-5,width-20,10)
	x = 10
	y = int(height/2.0)
	self.kfpixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
	x = width-10
	self.kfpixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
	# draw the keyframe circles
	for i in range(len(self.keyframes)):
	    # first the outer circle
	    x = self.keyframes[i]
	    if i == self.kfselected:
	        drawgc.set_foreground(pink)
	    else:
	        drawgc.set_foreground(darkgreen)
	    self.kfpixmap.draw_arc(drawgc,True,x-40,y-40,80,80,0,360*64)
	    # then the inner circle
	    drawgc.set_foreground(white)
	    self.kfpixmap.draw_arc(drawgc,True,x-35,y-35,70,70,0,360*64)
	    if self.kfssticks[i]:
	        # draw a man in the circle
	        drawgc.set_foreground(black)
	        hsize = self.kfssticks[i]['HEAD'][1]
	        rhsize = int(self.kfparts[i]['RIGHT HAND']*0.2)
	        lhsize = int(self.kfparts[i]['LEFT HAND']*0.2)
		self.drawstickman(drawgc,self.kfpixmap,(x,y),self.kfsjoints[i],hsize,rhsize,lhsize)
	        #self.kfpixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
        self.kfdraw.queue_draw()

    def drawfp(self):
        area = self.toplevel.window
	drawgc = area.new_gc()
	drawgc.line_width = 1
	cm = drawgc.get_colormap()
	red = cm.alloc_color('red')
	white = cm.alloc_color('white')
	black = cm.alloc_color('black')
	blue = cm.alloc_color('blue')
	green = cm.alloc_color('green')
	pink = cm.alloc_color(PINK)
	bgcolor = cm.alloc_color(BACKGROUND)
	darkgreen = cm.alloc_color(BUTTON_BACKGROUND)
	drawgc.fill = gtk.gdk.SOLID
        x, y, width, height = self.fpdraw.get_allocation()
        self.fppixmap = gtk.gdk.Pixmap(self.fpdraw.window, width, height)
	# clear area
	drawgc.set_foreground(white)
        self.fppixmap.draw_rectangle(drawgc,True,0,0,width,height)
	self.fpdraw.queue_draw()

    def inkeyframe(self, x, y):
        for i in range(len(self.keyframes)):
	    kx = self.keyframes[i]
	    if (abs(kx-x) <= 20):
	        return i
	return -1

    def injoint(self, x, y):
        for jname in self.joints:
	    jx, jy = self.joints[jname]
	    if (abs(jx-x) <= 5) and (abs(jy-y) <= 5):
	        return jname

    def inmiddle(self, x, y):
        mx, my = self.middle
	if (abs(mx-x) <= 5) and (abs(my-y) <= 5):
	    return True

    def inrotate(self, x, y):
        rx, ry = self.getrotatepoint()
	if (abs(rx-x) <= 5) and (abs(ry-y) <= 5):
	    return True

    def getrotatepoint(self):
        (angle,len) = self.sticks['TORSO']
	x,y = self.middle
	(rx,ry) = getpoints(x,y,angle,int(len/2.0))
	return (rx,ry)

    def selectstick(self, widget, event, data=None):
        if data:
	    if self.stickselected:
	        ebox = self.stickbuttons[self.stickselected]
	        ebox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
                label = ebox.get_child()
                label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_FOREGROUND))
	    self.stickselected = data
	    self.selectstickebox()

    def selectstickebox(self):
        ebox = self.stickbuttons[self.stickselected]
	ebox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_FOREGROUND))
        label = ebox.get_child()
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))
	if self.stickselected in self.sticks:
	    if self.stickselected == 'HEAD':
	        self.sizeentry.set_text(str(self.sticks[self.stickselected][1]*2))
	    else:
	        self.sizeentry.set_text(str(self.sticks[self.stickselected][1]))

	    self.angleentry.set_text(str(self.sticks[self.stickselected][0]))
	else:
	    # its a part not a stick
	    self.angleentry.set_text('-')
	    self.sizeentry.set_text(str(self.parts[self.stickselected]))

    def showlessonplans(self, widget, data=None):
        dia = gtk.Dialog(title='Lesson Plans',
	                 parent=None,
			 flags=0,
			 buttons=None)
	dia.set_default_size(500,500)
	dia.show()

	#dia.vbox.pack_start(scrolled_window, True, True, 0)
	notebook = gtk.Notebook()
	# uncomment below to highlight tabs
	notebook.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
	notebook.set_tab_pos(gtk.POS_TOP)
	#notebook.set_default_size(400,400)
	notebook.show()
        lessonplans = {}
	lpdir = os.path.join(self.mdirpath,LANG[self.language]['lpdir'])
	lpentries = os.listdir(lpdir)
	for entry in lpentries:
	    fpath = os.path.join(lpdir,entry)
	    lessonplans[entry] = getwrappedfile(fpath,95)
	lpkeys = lessonplans.keys()
	lpkeys.sort()
	for lpkey in lpkeys:
	    lpname = lpkey.replace('_',' ').replace('0','')[:-4]
	    label = gtk.Label(lessonplans[lpkey])
	    #if self.insugar:
	    #    label.modify_fg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
	    eb = gtk.EventBox()
	    eb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
	    #label.set_line_wrap(True)
	    label.show()
	    eb.add(label)
	    eb.show()
	    #tlabel = gtk.Label('Lesson Plan %s' % str(i+1))
	    tlabel = gtk.Label(lpname)
	    tlabel.show()
	    scrolled_window = gtk.ScrolledWindow()
	    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
	    scrolled_window.show()
	    scrolled_window.add_with_viewport(eb)
	    notebook.append_page(scrolled_window, tlabel)
	#dia.action_area.pack_start(notebook, True, True, 0)
	dia.vbox.pack_start(notebook, True, True, 0)
	result = dia.run()
	dia.destroy()

    def loadfile(self, widget, data=None):
        pass

    def savefile(self, widget, data=None):
        pass

    def exportanim(self, widget, data=None):
        if self.insugar:
	    self.exporttojournal()
	else:
	    self.exportfile()

    def exportfile(self):
        self.makeframes()
	fsecs = self.frames.keys()
	tmpdir = '/tmp'
	pngpaths = []
	for i in fsecs:
            joints = self.frames[i]
	    parts = self.fparts[i]
	    # draw on the main drawing area
            area = self.toplevel.window
	    drawgc = area.new_gc()
	    drawgc.line_width = 3
	    cm = drawgc.get_colormap()
	    white = cm.alloc_color('white')
	    black = cm.alloc_color('black')
	    drawgc.fill = gtk.gdk.SOLID
            x, y, width, height = self.mfdraw.get_allocation()
            pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
	    # clear area
	    drawgc.set_foreground(white)
            pixmap.draw_rectangle(drawgc,True,0,0,width,height)

	    drawgc.set_foreground(black)
	    #hsize = self.sticks['HEAD'][1] # really half of head size
	    hsize = self.fhsize[i]
	    middle = self.fmiddles[i]
	    rhsize = parts['RIGHT HAND']
	    lhsize = parts['LEFT HAND']
	    self.drawstickman(drawgc,pixmap,middle,joints,hsize,rhsize,lhsize)
	    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
	    gtk.gdk.Pixbuf.get_from_drawable(pixbuf,pixmap,pixmap.get_colormap(),0,0,0,0,width,height)
	    filename = 'fp%03d.png' % i
	    filepath = os.path.join(tmpdir,filename)
	    pixbuf.save(filepath,'png')
	    pngpaths.append(filepath)
	# now convert all of the pngs to gif and then make a gif animation
	convertpath = 'convert'
	tmpdir = '/tmp'
	entires = os.listdir(tmpdir)
	gifpaths = []
	for pngfilepath in pngpaths:
	    giffilepath = pngfilepath[:-4]+'.gif'
	    gifpaths.append(giffilepath)
	    os.system('%s %s %s' % (convertpath,pngfilepath,giffilepath))
	    #os.remove(pngfilepath)
	agifpath = os.path.join(self.mdirpath,'animatefp.gif')
	os.system('%s -delay 20 -loop 0 %s/fp*.gif %s' % (convertpath,tmpdir,agifpath))
	for giffilepath in gifpaths:
	    os.remove(giffilepath)

    def exporttojournal(self):
        self.makeframes()
	fsecs = self.frames.keys()
	tmpdir = '/tmp'
	pngpaths = []
	firstpixindex = fsecs[0]
	for i in [fsecs[0]]:
            joints = self.frames[i]
	    parts = self.fparts[i]
	    # draw on the main drawing area
            area = self.toplevel.window
	    drawgc = area.new_gc()
	    drawgc.line_width = 3
	    cm = drawgc.get_colormap()
	    white = cm.alloc_color('white')
	    black = cm.alloc_color('black')
	    drawgc.fill = gtk.gdk.SOLID
            x, y, width, height = self.mfdraw.get_allocation()
            pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
	    # clear area
	    drawgc.set_foreground(white)
            pixmap.draw_rectangle(drawgc,True,0,0,width,height)

	    drawgc.set_foreground(black)
	    #hsize = self.sticks['HEAD'][1] # really half of head size
	    hsize = self.fhsize[i]
	    middle = self.fmiddles[i]
	    rhsize = parts['RIGHT HAND']
	    lhsize = parts['LEFT HAND']
	    self.drawstickman(drawgc,pixmap,middle,joints,hsize,rhsize,lhsize)
	    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
	    if i == firstpixindex:
	        firstpixbuf = pixbuf
	    gtk.gdk.Pixbuf.get_from_drawable(pixbuf,pixmap,pixmap.get_colormap(),0,0,0,0,width,height)
	    filename = 'fp%03d.png' % i
	    filepath = os.path.join(tmpdir,filename)
	    pixbuf.save(filepath,'png')
	    pngpaths.append(filepath)
        from sugar.datastore import datastore
	mediaObject = datastore.create()
	mediaObject.metadata['title'] = 'FlipSticks PNG'
	thumbData = self._get_base64_pixbuf_data(firstpixbuf)
	mediaObject.metadata['preview'] = thumbData
	#medaiObject.metadata['icon-color'] = ''
	mediaObject.metadata['mime_type'] = 'image/png'
	mediaObject.file_path = pngpaths[0]
	datastore.write(mediaObject)

    def _get_base64_pixbuf_data(self, pixbuf):
	data = [""]
	pixbuf.save_to_callback(self._save_data_to_buffer_cb, "png", {}, data)
	import base64
	return base64.b64encode(str(data[0]))
    
    def _save_data_to_buffer_cb(self, buf, data):
	data[0] += buf
	return True
    
    def playbackwards(self, widget, data=None):
        if self.playing:
	    playimg = gtk.Image()
	    playimg.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
	    playimg.show()
	    widget.set_image(playimg)
	    self.playing = False
	    # set the main window to the keyframe
	    if self.kfsticks[self.kfselected]:
		self.sticks = self.kfsticks[self.kfselected].copy()
		self.parts = self.kfparts[self.kfselected].copy()
		self.middle = self.kfmiddles[self.kfselected]
		self.setjoints()
		self.drawmainframe()
	    self.updateentrybox()
	else:
	    stopimg = gtk.Image()
	    stopimg.set_from_file(os.path.join(self.iconsdir,'big_pause.png'))
	    stopimg.show()
	    widget.set_image(stopimg)
	    self.makeframes()
	    fsecs = self.frames.keys()
	    fsecs.sort()
	    if fsecs:
                self.playframenum = fsecs[-1]
	    else:
	        self.playframenum = -1
	    self.playingbackwards = True
	    self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def playforwards(self, widget, data=None):
        if self.playing:
	    playimg = gtk.Image()
	    playimg.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
	    playimg.show()
	    widget.set_image(playimg)
	    self.playing = False
	    # set the main window to the keyframe
	    if self.kfsticks[self.kfselected]:
		self.sticks = self.kfsticks[self.kfselected].copy()
		self.parts = self.kfparts[self.kfselected].copy()
		self.middle = self.kfmiddles[self.kfselected]
		self.setjoints()
		self.drawmainframe()
	    self.updateentrybox()
	else:
	    stopimg = gtk.Image()
	    stopimg.set_from_file(os.path.join(self.iconsdir,'big_pause.png'))
	    stopimg.show()
	    widget.set_image(stopimg)
	    self.makeframes()
	    #mkeys = self.fmiddles.keys()
	    #mkeys.sort()
	    #for mkey in mkeys:
	    #    print '%s:(%s,%s)' % (mkey,self.fmiddles[mkey][0],self.fmiddles[mkey][1])
	    fsecs = self.frames.keys()
	    fsecs.sort()
	    if fsecs:
                self.playframenum = fsecs[0]
	    else:
	        self.playframenum = -1
	    self.playingbackwards = False
	    self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def changed_cb(self, combobox):
        model = combobox.get_model()
	index = combobox.get_active()
	if index:
	    lang = model[index][0]
	    if lang == 'Espa\xc3\xb1ol':
	        lang = SPANISH
	    if lang in LANG:
	        self.lessonplans.set_label(LANG[lang]['lessonplan'])
		self.anglelabel.set_label(LANG[lang]['angle']+':')
		self.sizelabel.set_label(LANG[lang]['size']+':')
	        self.export.set_label(LANG[lang]['export'])
	        for stickpartname in self.labellist:
		    label = self.sticklabels[stickpartname] 
		    label.set_label(LANG[lang][stickpartname])
		prepare_btn(self.lessonplans)
		prepare_btn(self.export)
	return

    def setlastlanguage(self, widget, data=None):
        li = LANGLIST.index(self.language)
	if li == 0:
	    self.language = LANGLIST[len(LANGLIST)-1]
	else:
	    self.language = LANGLIST[li-1]
	self.changebuttonlang()

    def setnextlanguage(self, widget, data=None):
        li = LANGLIST.index(self.language)
	if li == (len(LANGLIST)-1):
	    self.language = LANGLIST[0]
	else:
	    self.language = LANGLIST[li+1]
	self.changebuttonlang()

    def getdefaultlang(self):
        return 'English'

    def getsdata(self):
        self.makeframes()
        sdd = {} # save data dictionary
	sdd['kfmiddles'] = self.kfmiddles
	sdd['kfparts'] = self.kfparts
	sdd['kfsticks'] = self.kfsticks
	sdd['kfssticks'] = self.kfssticks
	sdd['kfjoints'] = self.kfjoints
	sdd['kfsjoints'] = self.kfsjoints
	sdd['keyframes'] = self.keyframes
	sdd['kfselected'] = self.kfselected
        return pickle.dumps(sdd)

    def restore(self, sdata):
        sdd = pickle.loads(sdata)
	self.kfmiddles = sdd['kfmiddles']
	self.kfparts = sdd['kfparts']
	self.kfsticks = sdd['kfsticks']
	self.kfssticks = sdd['kfssticks']
	self.kfjoints = sdd['kfjoints']
	self.kfsjoints = sdd['kfsjoints']
	self.keyframes = sdd['keyframes']
	self.kfselected = sdd['kfselected']
        self.drawkeyframe()
	self.syncmaintokf()
        self.updateentrybox()

    def __init__(self, toplevel_window, mdirpath):
        self.insugar = False
        self.playing = False
	self.playingbackwards = False
	self.waittime = 3*150
	self.keyframe = 0
        self.toplevel = toplevel_window
        self.mdirpath = mdirpath
	xmiddle = int(DRAWWIDTH/2.0)
	ymiddle = int(DRAWHEIGHT/2.0)
	self.middle = (xmiddle,ymiddle)
	self.sticks = STICKS.copy()
	self.parts = PARTS.copy()
	self.sticklist = STICKLIST
	self.labellist = LABELLIST
	self.stickselected = 'RIGHT SHOULDER'
	self.laststickselected = None
	self.keyframes = KEYFRAMES
	self.kfsticks = [None,None,None,None,None]
	self.kfssticks = [None,None,None,None,None]
	self.kfjoints = [None,None,None,None,None]
	self.kfsjoints = [None,None,None,None,None]
	self.kfmiddles = [None,None,None,None,None]
	self.kfparts = [None,None,None,None,None]
	self.kfselected = 0
	self.joints = self.initjoints()
	self.setjoints()
	self.jointpressed = None
	self.kfpressed = -1
	self.middlepressed = False
	self.rotatepressed = False
	self.iconsdir = os.path.join(self.mdirpath,'icons')
	self.language = self.getdefaultlang()

        self.mpbox = gtk.VBox()
	self.main = gtk.EventBox()
	self.main.show()
        self.main.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.mainbox = gtk.EventBox()
	self.mainbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.mainbox.set_border_width(5)
	self.mainbox.show()
	self.main.add(self.mainbox)
        self.mpbox.show()
	self.hbox = gtk.HBox()
	self.hbox.show()
	self.vbox = gtk.VBox()
	self.vbox.show()
	self.hbox.pack_start(self.vbox,False,False,0)
	self.mainbox.add(self.mpbox)
	self.mpbox.pack_start(self.hbox,True,True,0)
	
	self.logobox = gtk.HBox(False,0)
	self.logobox.show()
	self.logo = gtk.Image()
	self.logo.show()
	self.logo.set_from_file(os.path.join(self.iconsdir,'logo.png'))
	self.logobox.pack_start(self.logo,False,False,0)
	self.lessonplans = gtk.Button('Lesson Plans')
	self.lessonplans.connect('clicked',self.showlessonplans, None)
	prepare_btn(self.lessonplans)
	self.lessonplans.show()
	self.lpvbox = gtk.VBox()
	self.lpvbox.show()
	self.lpvbox.pack_start(self.lessonplans,True,False,0)
	self.lpoframe = gtk.EventBox()
	self.lpoframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.lpoframe.show()
	self.lpframe = gtk.EventBox()
	self.lpframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.lpframe.show()
        self.lpalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	self.lpalign.add(self.lpframe)
	self.lpalign.set_padding(0,5,5,0)
	self.lpalign.show()
	self.lpoframe.add(self.lpalign)
	self.lphbox = gtk.HBox()
	self.lphbox.show()
	self.lphbox.pack_start(self.lpvbox,True,False,0)
	self.lpframe.add(self.lphbox)
	self.logobox.pack_start(self.lpoframe,True,True,0)
	#vvvvv LANGUAGE BUTTONS vvvvv
	#self.lastlang = gtk.Button()
	#self.lastlang.connect('clicked', self.setlastlanguage, None)
	#llla = gtk.Image()
	#llla.set_from_file(os.path.join(self.iconsdir,'left_arrow.png'))
	#llla.show()
	#self.lastlang.add(llla)
	#prepare_btn(self.lastlang)
	#self.lastlang.show()
	#self.llvbox = gtk.VBox()
	#self.llvbox.show()
	#self.llvbox.pack_start(self.lastlang,True,False,0)
	#self.lang = gtk.Button(self.language)
	#prepare_btn(self.lang)
	#self.lang.show()
	#self.nextlang = gtk.Button()
	#self.nextlang.connect('clicked', self.setnextlanguage, None)
	#nlra = gtk.Image()
	#nlra.set_from_file(os.path.join(self.iconsdir,'right_arrow.png'))
	#nlra.show()
	#self.nextlang.add(nlra)
	#prepare_btn(self.nextlang)
	#self.nextlang.show()
	#self.nlvbox = gtk.VBox()
	#self.nlvbox.show()
	#self.nlvbox.pack_start(self.nextlang,True,False,0)
	#self.langvbox = gtk.VBox()
	#self.langvbox.show()
	#self.langvbox.pack_start(self.lang,True,False,0)
	#^^^^^ LANGUAGE BUTTONS ^^^^^
        #vvvvv LANGUAGE DROPDOWN vvvvv
        self.langdd = gtk.combo_box_new_text()
	self.langdd.append_text('Language')
	self.langdd.append_text('English')
	self.langdd.append_text(SPANISH)
	self.langdd.connect('changed', self.changed_cb)
	self.langdd.set_active(0)
	self.langdd.show()
	self.langddvbox = gtk.VBox()
	self.langddvbox.show()
	self.langddvbox.pack_start(self.langdd,True,False,0)
	#^^^^^ LANGUAGE DROPDOWN ^^^^^
	self.langoframe = gtk.EventBox()
	self.langoframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.langoframe.show()
	self.langframe = gtk.EventBox()
	self.langframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.langframe.show()
	self.langalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	self.langalign.add(self.langframe)
	self.langalign.set_padding(0,5,5,5)
	self.langalign.show()
	self.langoframe.add(self.langalign)
	self.langhbox = gtk.HBox()
	self.langhbox.show()
	#self.langhbox.pack_start(self.llvbox,True,False,0)
	#self.langhbox.pack_start(self.langvbox,True,False,0)
	#self.langhbox.pack_start(self.nlvbox,True,False,0)
	self.langhbox.pack_start(self.langddvbox,True,False,0)
	self.langframe.add(self.langhbox)
	self.logobox.pack_start(self.langoframe,True,True,0)

	self.vbox.pack_start(self.logobox,False,False,0)

        #self.drawhbox = gtk.HBox()
	#self.drawhbox.show()
	self.mfdraw = gtk.DrawingArea()
	self.mfdraw.set_size_request(DRAWWIDTH,DRAWHEIGHT)
	self.mfdraw.show()
	self.mfdraw.connect('expose_event', self.expose_event)
	self.mfdraw.connect('configure_event', self.configure_event)
	self.mfdraw.connect('motion_notify_event', self.motion_notify_event)
	self.mfdraw.connect('button_press_event', self.button_press_event)
	self.mfdraw.connect('button_release_event', self.button_release_event)
	self.mfdraw.set_events(gtk.gdk.EXPOSURE_MASK
	                       | gtk.gdk.LEAVE_NOTIFY_MASK
			       | gtk.gdk.BUTTON_PRESS_MASK
			       | gtk.gdk.BUTTON_RELEASE_MASK
			       | gtk.gdk.POINTER_MOTION_MASK
			       | gtk.gdk.POINTER_MOTION_HINT_MASK)
	self.drawborder = gtk.EventBox()
	self.drawborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
	self.drawborder.set_border_width(10)
	self.drawborder.show()
	self.drawframe = gtk.EventBox()
	self.drawframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.drawframe.set_border_width(5)
	self.drawframe.show()
	self.drawborder.add(self.drawframe)
	self.drawframe.add(self.mfdraw)
	#self.drawhbox.pack_start(self.drawborder, False, False, 10)

	#self.vbox.pack_start(self.drawhbox,False,False,0)
	self.vbox.pack_start(self.drawborder,False,False,0)

        self.keyframehbox = gtk.HBox()
	self.keyframehbox.show()
	
	self.playback = gtk.Button()
	self.playback.connect('clicked', self.playbackwards, None)
	playbackla = gtk.Image()
	playbackla.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
	playbackla.show()
	self.playback.add(playbackla)
	prepare_btn(self.playback)
	self.playback.show()
	self.playbackvbox = gtk.VBox()
	self.playbackvbox.show()
	self.playbackvbox.pack_start(self.playback,True,False,0)
	self.keyframehbox.pack_start(self.playbackvbox,True,False,0)
	# vvvvvvvvvvKEYFRAME DRAWING AREA HEREvvvvvvvvvvvv
	self.kfdraw = gtk.DrawingArea()
	self.kfdraw.set_size_request(KEYFRAMEWIDTH,KEYFRAMEHEIGHT)
	self.kfdraw.show()
	self.kfdraw.connect('expose_event', self.kf_expose_event)
	self.kfdraw.connect('configure_event', self.kf_configure_event)
	self.kfdraw.connect('motion_notify_event', self.kf_motion_notify_event)
	self.kfdraw.connect('button_press_event', self.kf_button_press_event)
	self.kfdraw.connect('button_release_event', self.kf_button_release_event)
	self.kfdraw.set_events(gtk.gdk.EXPOSURE_MASK
	                       | gtk.gdk.LEAVE_NOTIFY_MASK
			       | gtk.gdk.BUTTON_PRESS_MASK
			       | gtk.gdk.BUTTON_RELEASE_MASK
			       | gtk.gdk.POINTER_MOTION_MASK
			       | gtk.gdk.POINTER_MOTION_HINT_MASK)
	#self.drawborder = gtk.EventBox()
	#self.drawborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
	#self.drawborder.show()
	#self.drawframe = gtk.EventBox()
	#self.drawframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	#self.drawframe.set_border_width(5)
	#self.drawframe.show()
	#self.drawborder.add(self.drawframe)
	#self.drawframe.add(self.mfdraw)
	self.keyframehbox.pack_start(self.kfdraw,False,False,0)

	# ^^^^^^^^^^KEYFRAME DRAWING AREA HERE^^^^^^^^^^^^
	self.playforward = gtk.Button()
	self.playforward.connect('clicked', self.playforwards, None)
	playforwardla = gtk.Image()
	playforwardla.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
	playforwardla.show()
	self.playforward.add(playforwardla)
	prepare_btn(self.playforward)
	self.playforward.show()
	self.playforwardvbox = gtk.VBox()
	self.playforwardvbox.show()
	self.playforwardvbox.pack_start(self.playforward,True,False,0)
	self.keyframehbox.pack_start(self.playforwardvbox,True,False,0)

	self.vbox.pack_start(self.keyframehbox,False,False,10)

	self.bottomcontrolshbox = gtk.HBox()
	self.bottomcontrolshbox.show()
	self.resetbutton = gtk.Button()
	resetimg = gtk.Image()
	resetimg.set_from_file(os.path.join(self.iconsdir,'reset.png'))
	resetimg.show()
	self.resetbutton.add(resetimg)
	self.resetbutton.connect('clicked', self.reset, None)
	prepare_btn(self.resetbutton)
	self.resetbutton.show()
	self.bottomcontrolshbox.pack_start(self.resetbutton, True, False, 0)

	self.setframebutton = gtk.Button()
	cameraimg = gtk.Image()
	cameraimg.set_from_file(os.path.join(self.iconsdir,'camera.png'))
	cameraimg.show()
	self.setframebutton.add(cameraimg)
	self.setframebutton.connect('clicked', self.setframe, None)
	prepare_btn(self.setframebutton)
	self.setframebutton.show()
	self.bottomcontrolshbox.pack_start(self.setframebutton, True, False, 0)

	self.clearframebutton = gtk.Button()
	clearimg = gtk.Image()
	clearimg.set_from_file(os.path.join(self.iconsdir,'clear.png'))
	clearimg.show()
	self.clearframebutton.add(clearimg)
	self.clearframebutton.connect('clicked', self.clearframe, None)
	prepare_btn(self.clearframebutton)
	self.clearframebutton.show()
	self.bottomcontrolshbox.pack_start(self.clearframebutton, True, False, 0)

	adj = gtk.Adjustment(2.5,1,5,.5,1)
	adj.connect('value_changed',self.setplayspeed)
	self.playspeed = gtk.HScale(adj)
	self.playspeed.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            self.playspeed.modify_bg(state, gtk.gdk.color_parse(color))
	self.playspeed.show()
	self.bottomcontrolshbox.pack_start(self.playspeed, True, True, 5)
	self.vbox.pack_start(self.bottomcontrolshbox,False,False,10)

        # NOW THE RIGHT SIDE
	self.rightvbox = gtk.VBox()
	self.rightvbox.show()
	# vvvvv FILE PICKER THING vvvvv
	#self.filechooserhbox = gtk.HBox()
	#self.filechooserhbox.show()
	#self.lastfile = gtk.Button()
	#lfla = gtk.Image()
	#lfla.set_from_file(os.path.join(self.iconsdir,'left_arrow.png'))
	#lfla.show()
	#self.lastfile.add(lfla)
	#prepare_btn(self.lastfile)
	#self.lastfile.show()
	#self.lfvbox = gtk.VBox()
	#self.lfvbox.show()
	#self.lfvbox.pack_start(self.lastfile,True,False,0)
	#self.filechooserhbox.pack_start(self.lfvbox,True,False,5)
        ## vvvvv FILE PICKER DRAWING AREA vvvvv
	#self.fpdraw = gtk.DrawingArea()
	#self.fpdraw.set_size_request(FPWIDTH,FPHEIGHT)
	#self.fpdraw.show()
	#self.fpdraw.connect('expose_event', self.fp_expose_event)
	#self.fpdraw.connect('configure_event', self.fp_configure_event)
	#self.fpdrawborder = gtk.EventBox()
	#self.fpdrawborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
	#self.fpdrawborder.show()
	#self.fpdrawframe = gtk.EventBox()
	#self.fpdrawframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	#self.fpdrawframe.set_border_width(5)
	#self.fpdrawframe.show()
	#self.fpdrawborder.add(self.fpdrawframe)
	#self.fpdrawframe.add(self.fpdraw)
	#self.filechooserhbox.pack_start(self.fpdrawborder,False,False,0)
        ## ^^^^^ FILE PICKER DRAWING AREA ^^^^^ 
	#self.nextfile = gtk.Button()
	#nfla = gtk.Image()
	#nfla.set_from_file(os.path.join(self.iconsdir,'right_arrow.png'))
	#nfla.show()
	#self.nextfile.add(nfla)
	#prepare_btn(self.nextfile)
	#self.nextfile.show()
	#self.nfvbox = gtk.VBox()
	#self.nfvbox.show()
	#self.nfvbox.pack_start(self.nextfile,True,False,0)
	#self.filechooserhbox.pack_start(self.nfvbox,True,False,5)
	#self.rightvbox.pack_start(self.filechooserhbox,False,False,5)
	# ADD FILENAME LABEL HERE
	# ^^^^^ FILE PICKER THING ^^^^^
	# START OF STICK CONTROLS
	self.stickcontrols = gtk.VBox()
	self.stickcontrols.show()
	self.stickcontrolsborder = gtk.EventBox()
	self.stickcontrolsborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
	self.stickcontrolsborder.set_border_width(5)
	self.stickcontrolsborder.show()
	self.stickcontrolsframe = gtk.EventBox()
	self.stickcontrolsframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
	self.stickcontrolsframe.set_border_width(5)
	self.stickcontrolsframe.show()
	self.stickcontrolsborder.add(self.stickcontrolsframe)
	self.stickcontrolsframe.add(self.stickcontrols)
	self.anglesizehbox = gtk.HBox()
	self.anglesizehbox.show()
	#label = gtk.Label('Angle:')
	self.anglelabel = gtk.Label(LANG[self.language]['angle']+':')
        self.anglelabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))
	self.anglelabel.show()
	self.anglesizehbox.pack_start(self.anglelabel,False,False,5)
	self.angleentry = gtk.Entry()
	self.angleentry.set_max_length(3)
	self.angleentry.set_width_chars(3)
	self.angleentry.connect('activate', self.enterangle_callback, self.angleentry)
	self.angleentry.show()
	self.anglesizehbox.pack_start(self.angleentry,False,False,0)
	#label = gtk.Label('Size:')
	self.sizelabel = gtk.Label(LANG[self.language]['size']+':')
        self.sizelabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))
	self.sizelabel.show()
	self.anglesizehbox.pack_start(self.sizelabel,False,False,5)
	self.sizeentry = gtk.Entry()
	self.sizeentry.set_max_length(3)
	self.sizeentry.set_width_chars(3)
	self.sizeentry.connect('activate', self.enterlen_callback, self.sizeentry)
	self.sizeentry.show()
	self.anglesizehbox.pack_start(self.sizeentry,False,False,0)
	self.asbox = gtk.EventBox()
	self.asbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_FOREGROUND))
	self.asbox.show()
	self.asbox.add(self.anglesizehbox)
	self.stickcontrols.pack_start(self.asbox,False,False,0)
	self.stickbuttons = {}
	self.sticklabels = {}
	for stickpartname in self.labellist:
	    #label = gtk.Label(capwords(stickpartname))
	    label = gtk.Label(LANG[self.language][stickpartname])
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_FOREGROUND))
	    label.show()
	    self.sticklabels[stickpartname] = label
	    ebox = gtk.EventBox()
	    ebox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
	    ebox.show()
	    ebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
	    ebox.connect('button_press_event',self.selectstick,stickpartname)
	    ebox.add(label)
	    self.stickbuttons[stickpartname] = ebox
	    self.stickcontrols.pack_start(ebox,False,False,0)
	# highlight the currently selected stick and update the entry boxes
	self.selectstickebox()
	# END OF STICK CONTROLS
        stickalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	stickalign.add(self.stickcontrolsborder)
	stickalign.set_padding(80,5,5,5) # top,bottom,left,right
	stickalign.show()
        self.rightvbox.pack_start(stickalign,False,False, 0)
        #self.rightvbox.pack_start(self.stickcontrolsborder,False,False, 0)
	#self.filesave = gtk.Button()
	#self.filesave.set_label('SAVE')
	#prepare_btn(self.filesave)
	#self.filesave.connect('clicked',self.savefile,None)
	#self.filesave.show()
	#self.fshbox = gtk.HBox()
	#self.fshbox.show()
	#self.fshbox.pack_start(self.filesave,True,False,0)
	#self.rightvbox.pack_start(self.fshbox,True,False,0)
	self.export = gtk.Button()
	#self.export.set_label('EXPORT')
	self.export.set_label(LANG[self.language]['export'])
	prepare_btn(self.export)
	self.export.connect('clicked',self.exportanim,None)
	self.export.show()
	self.exporthbox = gtk.HBox()
	self.exporthbox.show()
	self.exporthbox.pack_start(self.export,True,False,0)
	self.rightvbox.pack_start(self.exporthbox,True,False,0)

	self.hbox.pack_start(self.rightvbox,False,False,0)

try:
    from sugar.activity import activity
    from sugar.presence import presenceservice
    from sugar.presence.tubeconn import TubeConnection
    import telepathy
    import telepathy.client
    from dbus import Interface
    from dbus.service import method, signal
    from dbus.gobject_service import ExportedGObject

    class flipsticksActivity(activity.Activity):
        def __init__(self, handle):
            activity.Activity.__init__(self,handle)
            self.connect("destroy",self.destroy_cb)
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
	    self.app.insugar = True
            outerframe = gtk.EventBox()
	    outerframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
            outerframe.show()
            innerframe = gtk.EventBox()
            innerframe.show()
            ifalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	    ifalign.add(innerframe)
	    ifalign.set_padding(20,20,50,50) # top,bottom,left,right
	    ifalign.show()
            #innerframe.set_border_width(150)
            outerframe.add(ifalign)
            innerframe.add(self.app.main)
            self.set_canvas(outerframe)


            # mesh stuff
            self.pservice = presenceservice.get_instance()
            owner = self.pservice.get_owner()
            self.owner = owner
            try:
                name, path = self.pservice.get_preferred_connection()
                self.tp_conn_name = name
                self.tp_conn_path = path
                self.conn = telepathy.client.Connection(name, path)
            except TypeError:
	        pass
            self.initiating = None

	    #sharing stuff
	    self.game = None
	    self.connect('shared', self._shared_cb)
            if self._shared_activity:
                # we are joining the activity
                self.connect('joined', self._joined_cb)
                if self.get_shared():
                    # oh, OK, we've already joined
                    self._joined_cb()
            else:
                # we are creating the activity
		pass

        def destroy_cb(self, data=None):
            return True

	def read_file(self, filepath):
	    f = file(filepath)
	    sdata = f.read()
	    f.close()
	    self.app.restore(sdata)
	    
	def write_file(self, filepath):
	    sdata = self.app.getsdata()
	    f = open(filepath,'w')
	    f.write(sdata)
	    f.close()

	def _shared_cb(self,activity):
	    self.initiating = True
	    self._setup()
            id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
                  SERVICE, {})
	    #self.app.export.set_label('Shared Me')

	def _joined_cb(self,activity):
            if self.game is not None:
                return

            if not self._shared_activity:
                return

            #for buddy in self._shared_activity.get_joined_buddies():
            #    self.buddies_panel.add_watcher(buddy)

            #logger.debug('Joined an existing Connect game')
	    #self.app.export.set_label('Joined You')
            self.initiating = False
            self._setup()

            #logger.debug('This is not my activity: waiting for a tube...')
            self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
                reply_handler=self._list_tubes_reply_cb,
                error_handler=self._list_tubes_error_cb)

	def _setup(self):
            if self._shared_activity is None:
                return

            bus_name, conn_path, channel_paths = self._shared_activity.get_channels()

            # Work out what our room is called and whether we have Tubes already
            room = None
            tubes_chan = None
            text_chan = None
            for channel_path in channel_paths:
                channel = telepathy.client.Channel(bus_name, channel_path)
                htype, handle = channel.GetHandle()
                if htype == telepathy.HANDLE_TYPE_ROOM:
                    #logger.debug('Found our room: it has handle#%d "%s"',
                    #    handle, self.conn.InspectHandles(htype, [handle])[0])
                    room = handle
                    ctype = channel.GetChannelType()
                    if ctype == telepathy.CHANNEL_TYPE_TUBES:
                        #logger.debug('Found our Tubes channel at %s', channel_path)
                        tubes_chan = channel
                    elif ctype == telepathy.CHANNEL_TYPE_TEXT:
                        #logger.debug('Found our Text channel at %s', channel_path)
                        text_chan = channel

            if room is None:
                #logger.error("Presence service didn't create a room")
                return
            if text_chan is None:
                #logger.error("Presence service didn't create a text channel")
                return

            # Make sure we have a Tubes channel - PS doesn't yet provide one
            if tubes_chan is None:
                #logger.debug("Didn't find our Tubes channel, requesting one...")
                tubes_chan = self.conn.request_channel(telepathy.CHANNEL_TYPE_TUBES,
                    telepathy.HANDLE_TYPE_ROOM, room, True)

            self.tubes_chan = tubes_chan
            self.text_chan = text_chan

            tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube',
                self._new_tube_cb)

        def _list_tubes_reply_cb(self, tubes):
            for tube_info in tubes:
                self._new_tube_cb(*tube_info)

        def _list_tubes_error_cb(self, e):
            #logger.error('ListTubes() failed: %s', e)
	    pass

        def _new_tube_cb(self, id, initiator, type, service, params, state):
            #logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
            #             'params=%r state=%d', id, initiator, type, service,
            #             params, state)

            if (self.game is None and type == telepathy.TUBE_TYPE_DBUS and
                service == SERVICE):
                if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                    self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

                tube_conn = TubeConnection(self.conn,
                    self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                    id, group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
                self.game = ConnectGame(tube_conn, self.initiating, self)
    
    class ConnectGame(ExportedGObject):
        def __init__(self,tube, is_initiator, activity):
	    super(ConnectGame,self).__init__(tube,PATH)
	    self.tube = tube
	    self.is_initiator = is_initiator
	    self.entered = False
	    self.activity = activity

	    self.ordered_bus_names=[]
	    self.tube.watch_participants(self.participant_change_cb)

	def participant_change_cb(self, added, removed):
	    if not self.entered:
	        if self.is_initiator:
		    self.add_hello_handler()
		else:
		    self.Hello()
	    self.entered = True

	@signal(dbus_interface=IFACE,signature='')
        def Hello(self):
	    """Request that this player's Welcome method is called to bring it
	    up to date with the game state.
	    """

	@method(dbus_interface=IFACE, in_signature='s', out_signature='')
	def Welcome(self, sdata):
	    self.activity.app.restore(str(sdata))

	def add_hello_handler(self):
	    self.tube.add_signal_receiver(self.hello_cb, 'Hello', IFACE,
	        path=PATH, sender_keyword='sender')

        def hello_cb(self, sender=None):
	    self.tube.get_object(sender, PATH).Welcome(self.activity.app.getsdata(),dbus_interface=IFACE)

except ImportError:
    pass

if __name__ == '__main__':
    toplevel_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    mdirpath = os.path.abspath(os.curdir)
    app = flipsticks(toplevel_window,mdirpath)
    toplevel_window.add(app.main)
    toplevel_window.set_title('FlipSticks')
    toplevel_window.connect('delete_event', app.delete_event)
    toplevel_window.connect('destroy', app.destroy)
    toplevel_window.show()
    gtk.main()
