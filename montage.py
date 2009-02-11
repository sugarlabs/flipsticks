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

import os
import gtk
import math
import gobject
import logging
from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path

import model
import screen
import kinematic
import theme
from theme import *

logger = logging.getLogger('flipsticks')

class View(gtk.EventBox):
    __gsignals__ = {
        'frame-changed' : (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]) }

    def set_keyframe(self, value):
        i, key = value
        logger.debug('set_keyframe[%d]=%s' % (i, key and key.collect()))
        if not key:
            model.keys[i].clear()
        else:
            model.keys[i] = key
        self.restore()

    keyframe = gobject.property(type=object, getter=None, setter=set_keyframe)

    def reset(self):
        self.key.reset()
        self.selectstickebox()
        self.drawmainframe()

    def setframe(self):
        model.keys[self.kfselected].assign(self.key)
        self.drawkeyframe()
        self.emit('frame-changed', self.kfselected)

    def clearframe(self):
        model.keys[self.kfselected].clear()
        self.drawkeyframe()
        self.emit('frame-changed', self.kfselected)

    def setplayspeed(self, value):
        self.waittime = int((100-value)*5)
        if self.playing:
            gobject.source_remove(self.playing)
            self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def playbackwards(self):
        if self.playing:
            gobject.source_remove(self.playing)

        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        fsecs.sort()
        if fsecs:
            self.playframenum = fsecs[-1]
        else:
            self.playframenum = -1
        self.playingbackwards = True

        logger.debug('playbackwards speed=%s' % self.waittime)
        self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def playforwards(self):
        if self.playing:
            gobject.source_remove(self.playing)

        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        fsecs.sort()
        if fsecs:
            self.playframenum = fsecs[0]
        else:
            self.playframenum = -1

        logger.debug('playforwards speed=%s' % self.waittime)
        self.playingbackwards = False
        self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def stop(self):
        if not self.playing:
            return

        gobject.source_remove(self.playing)
        self.playing = None

        # set the main window to the keyframe
        if not model.keys[self.kfselected].empty():
            self.key.assign(model.keys[self.kfselected])
            self.drawmainframe()
        self.updateentrybox()

    def exportframe(self):
        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        firstpixindex = fsecs[0]

        x, y, width, height = self.mfdraw.get_allocation()
        pixmap = gtk.gdk.Pixmap(self.mfdraw.window, width, height)
        self._draw_frame(fsecs[0], pixmap)
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
        gtk.gdk.Pixbuf.get_from_drawable(pixbuf,pixmap,pixmap.get_colormap(),0,0,0,0,width,height)

        model.screen_shot(pixbuf)

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
                if _inarea(widget, x, y):
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
                if _inarea(widget, x, y):
                    xdiff = x-self.key.middle[0]
                    ydiff = y-self.key.middle[1]
                    self.key.move(xdiff, ydiff)
                    self.key.middle = (x,y)
                    self.drawmainframe()
            elif self.rotatepressed:
                if _inarea(widget, x, y):
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
                if _inarea(widget, x, y):
                    xdiff = int(x - self.kf_mouse_pos)
                    frame = model.keys[self.kfpressed]
                    if frame.x + xdiff > KEYFRAME_RADIUS \
                            and frame.x + xdiff < KEYFRAMEWIDTH-KEYFRAME_RADIUS:
                        frame.move(xdiff)

                        if self._emit_move_handle:
                            gobject.source_remove(self._emit_move_handle)
                            if self._emit_move_key != self.kfpressed:
                                self._emit_move(self._emit_move_key)

                        self._emit_move_key = self.kfpressed
                        self._emit_move_handle = gobject.timeout_add(
                                MOVEMIT_TIMEOUT, self._emit_move,
                                self.kfpressed)

                        self.drawkeyframe()
                    self.kf_mouse_pos = x
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
            kfnum = self._inkeyframe(event.x, event.y)
            if kfnum >= 0:
                self.kf_mouse_pos = event.x
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
            self.anglel_adj.set_value(newangle)
            self.anglel_slider.set_sensitive(True)
        else:
            # part not stick
            self.angleentry.set_text('')
            self.angleentry.set_sensitive(False)
            self.anglel_adj.set_value(0)
            self.anglel_slider.set_sensitive(False)

        self.key.setjoints()
        self.drawmainframe()

    def updateentrybox(self):
        if self.stickselected in self.key.sticks:
            (angle, len) = self.key.sticks[self.stickselected]
            self.angleentry.set_text(str(angle))
            self.anglel_adj.set_value(angle)
        else:
            # part not stick
            len = self.key.parts[self.stickselected]
        self.sizeentry.set_text(str(len))
        self.size_adj.set_value(len)

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

    def drawmainframe(self):
        if not self.pixmap:
            return

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
        for i in list(reversed(self.keys_overlap_stack)):
            # first the outer circle
            x = model.keys[i].x
            if i == self.kfselected:
                drawgc.set_foreground(pink)
            else:
                drawgc.set_foreground(darkgreen)
            self.kfpixmap.draw_arc(drawgc, True, x-KEYFRAME_RADIUS,
                    y-KEYFRAME_RADIUS, KEYFRAME_RADIUS*2, KEYFRAME_RADIUS*2,
                    0, 360*64)
            # then the inner circle
            drawgc.set_foreground(white)
            self.kfpixmap.draw_arc(drawgc, True, x-KEYFRAME_RADIUS+5,
                    y-KEYFRAME_RADIUS+5, (KEYFRAME_RADIUS-5)*2,
                    (KEYFRAME_RADIUS-5)*2, 0, 360*64)
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
                size = self.key.sticks[self.stickselected][1]*2
            else:
                size = self.key.sticks[self.stickselected][1]

            angle = self.key.sticks[self.stickselected][0]
            self.angleentry.set_text(str(angle))
            self.angleentry.set_sensitive(True)
            self.anglel_adj.set_value(angle)
            self.anglel_slider.set_sensitive(True)
        else:
            size = self.key.parts[self.stickselected]

            # its a part not a stick
            self.angleentry.set_text('')
            self.angleentry.set_sensitive(False)
            self.anglel_adj.set_value(0)
            self.anglel_slider.set_sensitive(False)

        self.sizeentry.set_text(str(size))
        self.size_adj.set_value(size)

    def __init__(self, activity):
        gtk.EventBox.__init__(self)

        self.playing = False
        self.playingbackwards = False
        self.toplevel = activity
        self.stickselected = 'RIGHT SHOULDER'
        self.pixmap = None
        self._emit_move_handle = None

        self.setplayspeed(50)

        self.keys_overlap_stack = []
        for i in range(len(model.keys)):
            self.keys_overlap_stack.append(i)

        self.key = screen.ScreenFrame()

        self.kfselected = 0
        self.jointpressed = None
        self.kfpressed = -1
        self.middlepressed = False
        self.rotatepressed = False
        self.iconsdir = os.path.join(get_bundle_path(), 'icons')

        # screen

        self.mfdraw = gtk.DrawingArea()
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
        self.mfdraw.set_size_request(DRAWWIDTH, DRAWHEIGHT)

        screen_box = gtk.EventBox()
        screen_box.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        screen_box.set_border_width(PAD/2)
        screen_box.add(self.mfdraw)

        screen_pink = gtk.EventBox()
        screen_pink.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        screen_pink.set_border_width(PAD)
        screen_pink.add(screen_box)

        # keyframes

        self.kfdraw = gtk.DrawingArea()
        self.kfdraw.set_size_request(KEYFRAMEWIDTH,KEYFRAMEHEIGHT)
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

        kfdraw_box = gtk.EventBox()
        kfdraw_box.set_border_width(PAD)
        kfdraw_box.add(self.kfdraw)

        # control box

        angle_box = gtk.HBox()
        anglelabel = gtk.Label(_('Angle:'))
        anglelabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))
        anglelabel.set_size_request(60, -1)
        angle_box.pack_start(anglelabel,False,False,5)
        self.angleentry = gtk.Entry()
        self.angleentry.set_max_length(3)
        self.angleentry.set_width_chars(3)
        self.angleentry.connect('activate', self.enterangle_callback, self.angleentry)
        self.angleentry.modify_bg(gtk.STATE_INSENSITIVE,
                gtk.gdk.color_parse(BUTTON_FOREGROUND))
        angle_box.pack_start(self.angleentry,False,False,0)
        self.anglel_adj = gtk.Adjustment(0, 0, 360, 1, 60, 0)
        self.anglel_adj.connect('value_changed', self._anglel_adj_cb)
        self.anglel_slider = gtk.HScale(self.anglel_adj)
        self.anglel_slider.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            self.anglel_slider.modify_bg(state, gtk.gdk.color_parse(color))
        angle_box.pack_start(self.anglel_slider)

        size_box = gtk.HBox()
        sizelabel = gtk.Label(_('Size:'))
        sizelabel.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))
        sizelabel.set_size_request(60, -1)
        size_box.pack_start(sizelabel,False,False,5)
        self.sizeentry = gtk.Entry()
        self.sizeentry.set_max_length(3)
        self.sizeentry.set_width_chars(3)
        self.sizeentry.connect('activate', self.enterlen_callback, self.sizeentry)
        self.sizeentry.modify_bg(gtk.STATE_INSENSITIVE,
                gtk.gdk.color_parse(BUTTON_FOREGROUND))
        size_box.pack_start(self.sizeentry,False,False,0)
        self.size_adj = gtk.Adjustment(0, 0, 200, 1, 30, 0)
        self.size_adj.connect('value_changed', self._size_adj_cb)
        size_slider = gtk.HScale(self.size_adj)
        size_slider.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            size_slider.modify_bg(state, gtk.gdk.color_parse(color))
        size_box.pack_start(size_slider)

        control_head_box = gtk.VBox()
        control_head_box.pack_start(angle_box)
        control_head_box.pack_start(size_box)

        control_head = gtk.EventBox()
        control_head.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_FOREGROUND))
        control_head.add(control_head_box)

        control_options = gtk.VBox()
        self.stickbuttons = {}
        self.sticklabels = {}
        for stickpartname in LABELLIST:
            label = gtk.Label(STRINGS[stickpartname])
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_FOREGROUND))
            self.sticklabels[stickpartname] = label
            ebox = gtk.EventBox()
            ebox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
            ebox.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            ebox.connect('button_press_event',self.selectstick,stickpartname)
            ebox.add(label)
            self.stickbuttons[stickpartname] = ebox
            control_options.pack_start(ebox,False,False,0)
        self.selectstickebox()

        control_scroll = gtk.ScrolledWindow()
        control_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        control_scroll.add_with_viewport(control_options)
        control_options.get_parent().modify_bg(gtk.STATE_NORMAL,
                gtk.gdk.color_parse(BUTTON_BACKGROUND))

        control_box = gtk.VBox()
        control_box.pack_start(control_head, False, False, 0)
        control_box.pack_start(control_scroll)

        control_bg = gtk.EventBox()
        control_bg.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
        control_bg.set_border_width(PAD/2)
        control_bg.add(control_box)

        control_pink = gtk.EventBox()
        control_pink.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        control_pink.set_border_width(PAD)
        control_pink.add(control_bg)

        # left control box

        logo = gtk.Image()
        logo.set_from_file(os.path.join(self.iconsdir,'logo.png'))

        leftbox = gtk.VBox()
        leftbox.pack_start(logo, False, False)
        leftbox.pack_start(control_pink)

        # desktop

        hdesktop = gtk.HBox()
        hdesktop.pack_start(leftbox, False)
        hdesktop.pack_start(screen_pink, False, False)

        desktop = gtk.VBox()
        desktop.pack_start(hdesktop)
        desktop.pack_start(kfdraw_box, False, False, 0)

        greenbox = gtk.EventBox()
        greenbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(PAD/2)
        greenbox.add(desktop)

        self.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        self.add(greenbox)
        self.show_all()

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

    def _inkeyframe(self, x, y):
        dy = math.pow(abs(y - KEYFRAMEHEIGHT/2), 2)

        for i, key in enumerate(self.keys_overlap_stack):
            dx = math.pow(abs(x - model.keys[key].x), 2)
            l = math.sqrt(dx + dy)
            if int(l) <= KEYFRAME_RADIUS:
                self.keys_overlap_stack.pop(i)
                self.keys_overlap_stack.insert(0, key)
                return key

        return -1

    def _anglel_adj_cb(self, adj):
        self.angleentry.set_text(str(int(adj.value)))
        self.enterangle_callback(None, self.angleentry)

    def _size_adj_cb(self, adj):
        self.sizeentry.set_text(str(int(adj.value)))
        self.enterlen_callback(None, self.sizeentry)

    def _emit_move(self, key):
        self._emit_move_handle = None
        self.emit('frame-changed', key)
        return False

def _inarea(widget, x, y):
    x_, y_, width, height = widget.get_allocation()
    if x < 0 or y < 0 or x >= width or y >= height:
        return False
    return True
