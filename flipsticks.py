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

import model
import screen
import kinematic
from theme import *

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

class flipsticks:
    def restore(self):
        self.drawkeyframe()
        self.syncmaintokf()
        self.updateentrybox()

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

    def configure_event(self, widget, event):
        x, y, width, height = self.mfdraw.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
        self.drawmainframe()
        return True

    def kf_configure_event(self, widget, event):
        self.drawkeyframe()
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
                if _inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
                    #self.key.joints[self.jointpressed] = (x,y) # old hack way
                    # first find the parents x,y
                    (px,py) = model.getparentjoint(self.jointpressed,self.key.joints,
                                                  self.key.middle)
                    if x-px == 0:
                        #computeangle = 0
                        b = 1
                    else:
                        b = float(px-x)
                    a = float(y-py)
                    computeangle = int(math.degrees(math.atan(a/b)))
                    stickname = JOINTTOSTICK[self.jointpressed]
                    # add sum of parent angles to new angle
                    parents = model.getparentsticks(stickname)
                    panglesum = 0
                    for parentname in parents:
                        (pangle,plen) = self.key.sticks[parentname]
                        panglesum += pangle
                    (angle, len) = self.key.sticks[stickname]
                    #print 'X:%s,Y:%s,PX:%s,PY:%s,ANGLE:%s,NEWANGLE:%s' % (x,y,px,py,angle,newangle)
                    newangle = computeangle-panglesum
                    if (x < px) or (b == 1):
                        newangle = newangle + 180
                    if newangle < 0:
                        newangle = 360 + newangle
                    self.key.sticks[stickname] = (newangle,len)
                    self.key.setjoints() # this is overkill
                    self.drawmainframe()
                    self.updateentrybox()
            elif self.middlepressed:
                if _inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
                    xdiff = x-self.key.middle[0]
                    ydiff = y-self.key.middle[1]
                    self.shiftjoints(xdiff,ydiff)
                    self.key.middle = (x,y)
                    self.drawmainframe()
            elif self.rotatepressed:
                if _inarea(x,y,DRAWWIDTH,DRAWHEIGHT):
                    (px,py) = self.key.middle
                    if x-px == 0:
                        #computeangle = 0
                        b = 1
                    else:
                        b = float(px-x)
                    a = float(y-py)
                    computeangle = int(math.degrees(math.atan(a/b)))
                    stickname = 'TORSO'
                    (angle, len) = self.key.sticks[stickname]
                    newangle = computeangle
                    if (x < px) or (b == 1):
                        newangle = newangle + 180
                    if newangle < 0:
                        newangle = 360 + newangle
                    anglediff = newangle-angle
                    self.key.sticks[stickname] = (newangle,len)
                    # now rotate the other sticks off of the middle
                    for stickname in ['NECK','RIGHT SHOULDER','LEFT SHOULDER']:
                        (sangle,slen) = self.key.sticks[stickname]
                        newsangle = sangle+anglediff
                        if newsangle < 0:
                            newsangle = 360 + newsangle
                        if newsangle > 360:
                            newsangle = newsangle - 360
                        self.key.sticks[stickname] = (newsangle,slen)
                    self.key.setjoints()
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
                if _inarea(x,y,KEYFRAMEWIDTH,KEYFRAMEHEIGHT):
                    xdiff = x - model.keys[self.kfpressed].x
                    self.shiftjoints(xdiff,0, model.keys[self.kfpressed].scaled_joints)
                    model.keys[self.kfpressed].x = x
                    self.drawkeyframe()
        return True

    def button_press_event(self, widget, event):
        if event.button == 1 and self.pixmap != None:
            joint = self.key.injoint(event.x, event.y)
            if joint:
                self.jointpressed = joint
                self.drawmainframe()
            elif self.key.inmiddle(event.x, event.y):
                self.middlepressed = True
                self.drawmainframe()
            elif self.key.inrotate(event.x, event.y):
                self.rotatepressed = True
                self.drawmainframe()
        return True

    def syncmaintokf(self):
        # set the main window to the keyframe
        if not model.keys[self.kfselected].empty():
            self.key.assign(model.keys[self.kfselected])
            self.drawmainframe()

    def kf_button_press_event(self, widget, event):
        if event.button == 1 and self.pixmap != None:
            kfnum = _inkeyframe(event.x, event.y)
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

        self._draw_frame(self.playframenum, self.pixmap)
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
        if stickname in self.key.sticks:
            newangle = int(entry.get_text())
            (angle, len) = self.key.sticks[stickname]
            self.key.sticks[stickname] = (newangle,len)
        else:
            # part not stick
            self.angleentry.set_text('-')
        self.key.setjoints()
        self.drawmainframe()

    def updateentrybox(self):
        if self.stickselected in self.key.sticks:
            (angle, len) = self.key.sticks[self.stickselected]
            self.angleentry.set_text(str(angle))
        else:
            # part not stick
            len = self.key.parts[self.stickselected]
        self.sizeentry.set_text(str(len))

    def enterlen_callback(self, widget, entry):
        stickname = self.stickselected
        newlen = int(entry.get_text())
        if stickname in self.key.sticks:
            if stickname == 'HEAD':
                newlen = int(newlen/2.0)
            (angle, len) = self.key.sticks[stickname]
            self.key.sticks[stickname] = (angle,newlen)
        else:
            # part not stick
            self.key.parts[stickname] = newlen
        self.key.setjoints()
        self.drawmainframe()

    def reset(self, widget, data=None):
        self.key.reset()
        self.selectstickebox()
        self.drawmainframe()

    def setframe(self, widget, data=None):
        model.keys[self.kfselected].assign(self.key)
        self.drawkeyframe()

    def clearframe(self, widget, data=None):
        model.keys[self.kfselected].clear()
        self.drawkeyframe()

    def shiftjoints(self,xdiff,ydiff,joints=None):
        if not joints:
            joints = self.key.joints
        for jname in joints:
            #if isinstance(self.key.joints[jname],tuple):
            (jx,jy) = joints[jname]
            njx = jx + xdiff
            njy = jy + ydiff
            joints[jname] = (njx,njy)

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
        hsize = self.key.sticks['HEAD'][1] # really half of head size
        rhsize = self.key.parts['RIGHT HAND']
        lhsize = self.key.parts['LEFT HAND']
        self.drawstickman(drawgc,self.pixmap,self.key.middle,self.key.joints,hsize,rhsize,lhsize)
        # draw circle for middle
        drawgc.set_foreground(green)
        if self.middlepressed:
            drawgc.set_foreground(blue)
        x,y = self.key.middle
        self.pixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
        # draw circle for rotate (should be halfway between middle and groin
        (rx,ry) = self.key.getrotatepoint()
        drawgc.set_foreground(yellow)
        if self.rotatepressed:
            drawgc.set_foreground(blue)
        self.pixmap.draw_arc(drawgc,True,rx-5,ry-5,10,10,0,360*64)
        # draw circles for joints
        drawgc.set_foreground(black)
        for jname in self.key.joints:
            if jname == 'head':
               continue
            x,y = self.key.joints[jname]
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
        for i in range(len(model.keys)):
            # first the outer circle
            x = model.keys[i].x
            if i == self.kfselected:
                drawgc.set_foreground(pink)
            else:
                drawgc.set_foreground(darkgreen)
            self.kfpixmap.draw_arc(drawgc,True,x-40,y-40,80,80,0,360*64)
            # then the inner circle
            drawgc.set_foreground(white)
            self.kfpixmap.draw_arc(drawgc,True,x-35,y-35,70,70,0,360*64)
            if model.keys[i].scaled_sticks:
                # draw a man in the circle
                drawgc.set_foreground(black)
                hsize = model.keys[i].scaled_sticks['HEAD'][1]
                rhsize = int(model.keys[i].parts['RIGHT HAND']*0.2)
                lhsize = int(model.keys[i].parts['LEFT HAND']*0.2)
                self.drawstickman(drawgc,self.kfpixmap,(x,y), model.keys[i].scaled_joints,hsize,rhsize,lhsize)
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
        if self.stickselected in self.key.sticks:
            if self.stickselected == 'HEAD':
                self.sizeentry.set_text(str(self.key.sticks[self.stickselected][1]*2))
            else:
                self.sizeentry.set_text(str(self.key.sticks[self.stickselected][1]))

            self.angleentry.set_text(str(self.key.sticks[self.stickselected][0]))
        else:
            # its a part not a stick
            self.angleentry.set_text('-')
            self.sizeentry.set_text(str(self.key.parts[self.stickselected]))

    def exportanim(self, widget, data=None):
        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        firstpixindex = fsecs[0]

        x, y, width, height = self.mfdraw.get_allocation()
        pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
        self._draw_frame(fsecs[0], pixmap)
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        gtk.gdk.Pixbuf.get_from_drawable(pixbuf,pixmap,pixmap.get_colormap(),0,0,0,0,width,height)

        model.screen_shot(pixbuf)

    def playbackwards(self, widget, data=None):
        if self.playing:
            playimg = gtk.Image()
            playimg.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
            playimg.show()
            widget.set_image(playimg)
            self.playing = False
            # set the main window to the keyframe
            if model.keys[self.kfselected]:
                self.key.assign(model.keys[self.kfselected])
                self.drawmainframe()
            self.updateentrybox()
        else:
            stopimg = gtk.Image()
            stopimg.set_from_file(os.path.join(self.iconsdir,'big_pause.png'))
            stopimg.show()
            widget.set_image(stopimg)
            self.frames = kinematic.makeframes()
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
            if model.keys[self.kfselected]:
                self.key.assign(model.keys[self.kfselected])
                self.drawmainframe()
            self.updateentrybox()
        else:
            stopimg = gtk.Image()
            stopimg.set_from_file(os.path.join(self.iconsdir,'big_pause.png'))
            stopimg.show()
            widget.set_image(stopimg)
            self.frames = kinematic.makeframes()
            fsecs = self.frames.keys()
            fsecs.sort()
            if fsecs:
                self.playframenum = fsecs[0]
            else:
                self.playframenum = -1
            self.playingbackwards = False
            self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def __init__(self, toplevel_window, mdirpath):
        self.playing = False
        self.playingbackwards = False
        self.waittime = 3*150
        self.keyframe = 0
        self.toplevel = toplevel_window
        self.mdirpath = mdirpath
        self.stickselected = 'RIGHT SHOULDER'

        self.key = screen.ScreenFrame()

        self.kfselected = 0
        self.jointpressed = None
        self.kfpressed = -1
        self.middlepressed = False
        self.rotatepressed = False
        self.iconsdir = os.path.join(self.mdirpath,'icons')
        self.language = 'English'

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
        
        self.logo = gtk.Image()
        self.logo.show()
        self.logo.set_from_file(os.path.join(self.iconsdir,'logo.png'))

        self.vbox.pack_start(self.logo,False,False,0)

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
        self.vbox.pack_start(self.drawborder,True,False,0)

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
        for stickpartname in LABELLIST:
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
        self.export = gtk.Button()
        self.export.set_label(LANG[self.language]['export'])
        prepare_btn(self.export)
        self.export.connect('clicked',self.exportanim,None)
        self.export.show()
        self.exporthbox = gtk.HBox()
        self.exporthbox.show()
        self.exporthbox.pack_start(self.export,True,False,0)
        self.rightvbox.pack_start(self.exporthbox,True,False,0)

        self.hbox.pack_start(self.rightvbox,False,False,0)

    def _draw_frame(self, index, pixmap):
        joints = self.frames[index].joints
        parts = self.frames[index].parts
        # draw on the main drawing area
        area = self.toplevel.window
        drawgc = area.new_gc()
        drawgc.line_width = 3
        cm = drawgc.get_colormap()
        white = cm.alloc_color('white')
        black = cm.alloc_color('black')
        drawgc.fill = gtk.gdk.SOLID
        x, y, width, height = self.mfdraw.get_allocation()
        #pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
        # clear area
        drawgc.set_foreground(white)
        pixmap.draw_rectangle(drawgc,True,0,0,width,height)

        drawgc.set_foreground(black)
        #hsize = self.key.sticks['HEAD'][1] # really half of head size
        hsize = self.frames[index].hsize
        middle = self.frames[index].middle
        rhsize = parts['RIGHT HAND']
        lhsize = parts['LEFT HAND']
        self.drawstickman(drawgc, pixmap, middle, joints, hsize, rhsize, lhsize)

def _inarea(x,y,awidth,aheight):
    if x+5 > awidth:
        return False
    if y+5 > aheight:
        return False
    if y < 5:
        return False
    if x < 5:
        return False
    return True

def _inkeyframe(x, y):
    for i in range(len(model.keys)):
        kx = model.keys[i].x
        if (abs(kx-x) <= 20):
            return i
    return -1
