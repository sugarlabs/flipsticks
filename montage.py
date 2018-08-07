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
from gi.repository import Gtk
from gi.repository import GObject
import cairo
import math
import logging
from gettext import gettext as _

from sugar3.activity.activity import get_bundle_path
from math import pi
import model
import screenflip
import kinematic
import theme
from theme import *

logger = logging.getLogger('flipsticks')


class View(Gtk.EventBox):
    __gsignals__ = {
        'frame-changed': (GObject.SIGNAL_RUN_FIRST, None, [GObject.TYPE_PYOBJECT])}

    def set_keyframe(self, value):
        i, key = value
        logger.debug('set_keyframe[%d]=%s' % (i, key and key.collect()))
        if not key:
            model.keys[i].clear()
        else:
            model.keys[i] = key
        self.restore()

    keyframe = GObject.property(type=object, getter=None, setter=set_keyframe)

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
        self.waittime = int((100 - value) * 5)
        if self.playing:
            GObject.source_remove(self.playing)
            self.playing = GObject.timeout_add(self.waittime, self.playframe)

    def playbackwards(self):
        if self.playing:
            GObject.source_remove(self.playing)

        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        fsecs.sort()
        if fsecs:
            self.playframenum = fsecs[-1]
        else:
            self.playframenum = -1
        self.playingbackwards = True

        logger.debug('playbackwards speed=%s' % self.waittime)
        self.playing = GObject.timeout_add(self.waittime, self.playframe)

    def playforwards(self):
        if self.playing:
            GObject.source_remove(self.playing)

        self.frames = kinematic.makeframes()
        fsecs = self.frames.keys()
        fsecs.sort()
        if fsecs:
            self.playframenum = fsecs[0]
        else:
            self.playframenum = -1

        logger.debug('playforwards speed=%s' % self.waittime)
        self.playingbackwards = False
        self.playing = GObject.timeout_add(self.waittime, self.playframe)

    def stop(self):
        if not self.playing:
            return

        GObject.source_remove(self.playing)
        self.playing = None

        # set the main window to the keyframe
        if not model.keys[self.kfselected].empty():
            self.key.assign(model.keys[self.kfselected])
            self.drawmainframe()
        self.updateentrybox()

    def exportframe(self):
        self.frames = kinematic.makeframes()
        if not self.frames:
            return
        firstpixindex = self.frames.keys()[0]

        width = self.window.get_width()
        height = self.window.get_height()
        surface = self.mfdraw.get_window().create_similar_surface(Gdk.Content.ColorAlpha, width, height)
        self._draw_frame(firstpixindex, surface)
        pixbuf = GdkPixbuf.Pixbuf(GdkPixbuf.Colorspace.RGB, False, 8, width, height)
        GdkPixbuf.Pixbuf.get_from_drawable(pixbuf, surface, surface.get_colormap(), 0, 0, 0, 0, width, height)

        model.screen_shot(pixbuf)

    def restore(self):
        self.drawkeyframe()
        self.syncmaintokf()
        self.updateentrybox()

    def __draw_cb(self, widget, cr):
        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()
        return False

    def __kf_draw_cb(self, widget, cr):
        cr.set_source_surface(self.kfsurface, 0, 0)
        cr.paint()
        return False

    def configure_event(self, widget, event):
        width = self.mfdraw.get_allocated_width()
        height = self.mfdraw.get_allocated_height()
        self.surface = self.mfdraw.get_window().create_similar_surface(cairo.CONTENT_COLOR, width, height)
        self.drawmainframe()
        return True

    def kf_configure_event(self, widget, event):
        self.drawkeyframe()
        return True

    def motion_notify_event(self, widget, event):
        if event.is_hint:
            (win, x, y, state) = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.get_state()
        if state & Gdk.ModifierType.BUTTON1_MASK and self.surface != None:
            if self.jointpressed:
                if _inarea(widget, x, y):
                    #self.key.joints[self.jointpressed] = (x,y) # old hack way
                    # first find the parents x,y
                    (px, py) = model.getparentjoint(self.jointpressed, self.key.joints,
                                                  self.key.middle)
                    if x - px == 0:
                        #computeangle = 0
                        b = 1
                    else:
                        b = float(px - x)
                    a = float(y - py)
                    computeangle = int(math.degrees(math.atan(a / b)))
                    stickname = JOINTTOSTICK[self.jointpressed]
                    # add sum of parent angles to new angle
                    parents = model.getparentsticks(stickname)
                    panglesum = 0
                    for parentname in parents:
                        (pangle, plen) = self.key.sticks[parentname]
                        panglesum += pangle
                    (angle, len) = self.key.sticks[stickname]
                    #print 'X:%s,Y:%s,PX:%s,PY:%s,ANGLE:%s,NEWANGLE:%s' % (x,y,px,py,angle,newangle)
                    newangle = computeangle - panglesum
                    if (x < px) or (b == 1):
                        newangle = newangle + 180
                    if newangle < 0:
                        newangle = 360 + newangle
                    self.key.sticks[stickname] = (newangle, len)
                    self.key.setjoints()  # this is overkill
                    self.drawmainframe()
                    self.updateentrybox()
            elif self.middlepressed:
                if _inarea(widget, x, y):
                    xdiff = x - self.key.middle[0]
                    ydiff = y - self.key.middle[1]
                    self.key.move(xdiff, ydiff)
                    self.key.middle = (x, y)
                    self.drawmainframe()
            elif self.rotatepressed:
                if _inarea(widget, x, y):
                    (px, py) = self.key.middle
                    if x - px == 0:
                        #computeangle = 0
                        b = 1
                    else:
                        b = float(px - x)
                    a = float(y - py)
                    computeangle = int(math.degrees(math.atan(a / b)))
                    stickname = 'TORSO'
                    (angle, len) = self.key.sticks[stickname]
                    newangle = computeangle
                    if (x < px) or (b == 1):
                        newangle = newangle + 180
                    if newangle < 0:
                        newangle = 360 + newangle
                    anglediff = newangle - angle
                    self.key.sticks[stickname] = (newangle, len)
                    # now rotate the other sticks off of the middle
                    for stickname in ['NECK', 'RIGHT SHOULDER', 'LEFT SHOULDER']:
                        (sangle, slen) = self.key.sticks[stickname]
                        newsangle = sangle + anglediff
                        if newsangle < 0:
                            newsangle = 360 + newsangle
                        if newsangle > 360:
                            newsangle = newsangle - 360
                        self.key.sticks[stickname] = (newsangle, slen)
                    self.key.setjoints()
                    self.drawmainframe()
                    self.updateentrybox()
                    
        return True

    def kf_motion_notify_event(self, widget, event):
        if event.is_hint:
            (win, x, y, state) = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.get_state()
        if state & Gdk.ModifierType.BUTTON1_MASK and self.surface != None:
            if self.kfpressed >= 0:
                if _inarea(widget, x, y):
                    xdiff = int(x - self.kf_mouse_pos)
                    frame = model.keys[self.kfpressed]
                    if frame.x + xdiff > KEYFRAME_RADIUS \
                            and frame.x + xdiff < KEYFRAMEWIDTH - KEYFRAME_RADIUS:
                        frame.move(xdiff)

                        if self._emit_move_handle:
                            GObject.source_remove(self._emit_move_handle)
                            if self._emit_move_key != self.kfpressed:
                                self._emit_move(self._emit_move_key)

                        self._emit_move_key = self.kfpressed
                        self._emit_move_handle = GObject.timeout_add(
                                MOVEMIT_TIMEOUT, self._emit_move,
                                self.kfpressed)

                        self.drawkeyframe()
                    self.kf_mouse_pos = x
        return True

    def button_press_event(self, widget, event):
        if event.button == 1 and self.surface != None:
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
        if event.button == 1 and self.surface != None:
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

        self._draw_frame(self.playframenum, self.surface)
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
                self.playframenum = fsecs[i - 1]
        else:
            # increment playframenum
            if self.playframenum == fsecs[-1]:
                self.playframenum = fsecs[0]
            else:
                i = fsecs.index(self.playframenum)
                self.playframenum = fsecs[i + 1]
        if self.playing:
            return True
        else:
            return False

    def enterangle_callback(self, widget, entry):
        stickname = self.stickselected
        if stickname in self.key.sticks:
            newangle = int(entry.get_text())
            (angle, len) = self.key.sticks[stickname]
            self.key.sticks[stickname] = (newangle, len)
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
            (angle, len) = self.key.sticks[stickname]
            self.key.sticks[stickname] = (angle, newlen)
        else:
            # part not stick
            self.key.parts[stickname] = newlen
        self.key.setjoints()
        self.drawmainframe()

    def drawmainframe(self):
        if not self.surface:
            return

        area = self.toplevel.get_window()
        drawgc = cairo.Context(self.surface)
        drawgc.set_line_width(3)
        red = Gdk.Color.parse('red')[1]
        yellow = Gdk.Color.parse('yellow')[1]
        white = Gdk.Color.parse('white')[1]
        black = Gdk.Color.parse('black')[1]
        blue = Gdk.Color.parse('blue')[1]
        green = Gdk.Color.parse('green')[1]
        width = self.mfdraw.get_allocated_width()
        height = self.mfdraw.get_allocated_height()
        #self.pixmap = Gdk.Pixmap(self.mfdraw.window, width, height)
        # clear area
        drawgc.set_source_rgb(white.red, white.green, white.blue)
        drawgc.rectangle(0, 0, width, height)
        drawgc.fill()

        drawgc.set_source_rgb(black.red, black.green, black.blue)
        hsize = self.key.sticks['HEAD'][1]  # really half of head size
        rhsize = self.key.parts['RIGHT HAND']
        lhsize = self.key.parts['LEFT HAND']
        self.drawstickman(drawgc, self.surface, self.key.middle, self.key.joints, hsize, rhsize, lhsize)
        # draw circle for middle
        drawgc.set_source_rgb(green.red, green.green, green.blue)
        if self.middlepressed:
            drawgc.set_source_rgb(blue.red, blue.green, blue.blue)
        x, y = self.key.middle
        drawgc.arc(x, y, 5, 0, 2*pi)
        drawgc.fill()
        # draw circle for rotate (should be halfway between middle and groin
        (rx, ry) = self.key.getrotatepoint()
        drawgc.set_source_rgb(yellow.red, yellow.green, yellow.blue)
        if self.rotatepressed:
            drawgc.set_source_rgb(blue.red, blue.green, blue.blue)
        drawgc.arc(rx, ry, 5, 0, 2*pi)
        drawgc.fill()
        # draw circles for joints
        drawgc.set_source_rgb(black.red, black.green, black.blue)
        for jname in self.key.joints:
            if jname == 'head':
                    continue
            x, y = self.key.joints[jname]
            if self.jointpressed == jname:
                drawgc.set_source_rgb(blue.red, blue.green, blue.blue)
                drawgc.arc(x, y, 5, 0, 2*pi)
                drawgc.fill()
                drawgc.set_source_rgb(black.red, black.green, black.blue)
            else:
                drawgc.set_source_rgb(red.red, red.green, red.blue)
                drawgc.arc(x, y, 5, 0, 2*pi)
                drawgc.fill()
                drawgc.set_source_rgb(black.red, black.green, black.blue)
        self.mfdraw.queue_draw()

    def drawstickman(self, drawgc, pixmap, middle, joints, hsize, rhsize, lhsize):
        leftarm = [middle, joints['leftshoulder'], joints['leftelbow'], joints['lefthand']]
        rightarm = [middle, joints['rightshoulder'], joints['rightelbow'], joints['righthand']]
        torso = [joints['neck'], middle, joints['groin']]
        leftleg = [joints['groin'], joints['lefthip'], joints['leftknee'],
                   joints['leftheel'], joints['lefttoe']]
        rightleg = [joints['groin'], joints['righthip'], joints['rightknee'],
                    joints['rightheel'], joints['righttoe']]
        # draw lines
        for i in range(len(leftarm)-1):
            drawgc.move_to(leftarm[i][0], leftarm[i][1])
            drawgc.line_to(leftarm[i+1][0], leftarm[i+1][1])
            drawgc.stroke()
        for i in range(len(rightarm)-1):
            drawgc.move_to(rightarm[i][0], rightarm[i][1])
            drawgc.line_to(rightarm[i+1][0], rightarm[i+1][1])
            drawgc.stroke()
        for i in range(len(torso)-1):
            drawgc.move_to(torso[i][0], torso[i][1])
            drawgc.line_to(torso[i+1][0], torso[i+1][1])
            drawgc.stroke()
        for i in range(len(leftleg)-1):
            drawgc.move_to(leftleg[i][0], leftleg[i][1])
            drawgc.line_to(leftleg[i+1][0], leftleg[i+1][1])
            drawgc.stroke()
        for i in range(len(rightleg)-1):
            drawgc.move_to(rightleg[i][0], rightleg[i][1])
            drawgc.line_to(rightleg[i+1][0], rightleg[i+1][1])
            drawgc.stroke()
        # draw head
        x, y = joints['head']
        drawgc.arc(x, y, hsize, 0, 2*pi)
        drawgc.fill()
        # draw circles for hands
        x, y = joints['righthand']
        drawgc.arc(x, y, int(rhsize/2.0), 0, 2*pi)
        drawgc.fill()
        x, y = joints['lefthand']
        drawgc.arc(x, y, int(lhsize/2.0), 0, 2*pi)
        drawgc.fill()

    def drawkeyframe(self):
        area = self.toplevel.get_window()
        width = self.kfdraw.get_allocated_width()
        height = self.kfdraw.get_allocated_height()
        self.kfsurface = self.kfdraw.get_window().create_similar_surface(cairo.CONTENT_COLOR, width, height)
        drawgc = cairo.Context(self.kfsurface)
        drawgc.set_line_width(2)
        red = Gdk.Color.parse('red')[1]
        yellow = Gdk.Color.parse('yellow')[1]
        white = Gdk.Color.parse('white')[1]
        black = Gdk.Color.parse('black')[1]
        blue = Gdk.Color.parse('blue')[1]
        green = Gdk.Color.parse('green')[1]
        pink = Gdk.Color.parse(PINK)[1]
        bgcolor = Gdk.Color.parse(BACKGROUND)[1]
        darkgreen = Gdk.Color.parse(BUTTON_BACKGROUND)[1]
        # clear area
        drawgc.set_source_rgb((1/65536.0)*bgcolor.red, (1/65536.0)*bgcolor.green, (1/65536.0)*bgcolor.blue)
        drawgc.rectangle(0, 0, width, height)
        drawgc.fill()
        # draw line in middle
        drawgc.set_source_rgb((1/65536.0)*darkgreen.red, (1/65536.0)*darkgreen.green, (1/65536.0)*darkgreen.blue)
        drawgc.rectangle(10, int(height / 2.0) - 5, width - 20, 10)
        drawgc.fill()
        x = 10
        y = int(height / 2.0)
        drawgc.arc(x, y, 5, 0, 2*pi)
        drawgc.fill()
        x = width - 10
        drawgc.arc(x, y, 5, 0, 2*pi)
        drawgc.fill()

        # draw the keyframe circles
        for i in list(reversed(self.keys_overlap_stack)):
            # first the outer circle
            x = model.keys[i].x
            if i == self.kfselected:
                drawgc.set_source_rgb((1/65536.0)*pink.red, (1/65536.0)*pink.green, (1/65536.0)*pink.blue)

            else:
                drawgc.set_source_rgb((1/65536.0)*darkgreen.red, (1/65536.0)*darkgreen.green, (1/65536.0)*darkgreen.blue)
            drawgc.set_line_width(5)
            drawgc.arc(x, y, KEYFRAME_RADIUS-2, 0, 2*pi)
            drawgc.stroke()
            # then the inner circle
            drawgc.set_source_rgb(white.red, white.green, white.blue)
            drawgc.arc(x, y, (KEYFRAME_RADIUS - 5), 0, 2*pi)
            drawgc.fill()
            if model.keys[i].scaled_sticks:
                # draw a man in the circle
                drawgc.set_source_rgb(black.red, black.green, black.blue)
                hsize = model.keys[i].scaled_sticks['HEAD'][1]
                rhsize = int(model.keys[i].parts['RIGHT HAND'] * 0.2)
                lhsize = int(model.keys[i].parts['LEFT HAND'] * 0.2)
                self.drawstickman(drawgc, self.kfsurface, (x, y), model.keys[i].scaled_joints, hsize, rhsize, lhsize)
                #self.kfpixmap.draw_arc(drawgc,True,x-5,y-5,10,10,0,360*64)
        self.kfdraw.queue_draw()

    def drawfp(self):
        area = self.toplevel.get_window()
        width = self.fpdraw.get_allocated_width()
        height = self.fpdraw.get_allocated_height()
        self.fpsurface = self.fpdraw.get_window().create_similar_surface(cairo.CONTENT_COLOR, width, height)
        drawgc = cairo.Context(self.fpsurface)
        drawgc.set_line_width(1)
        red = Gdk.Color.parse('red')[1]
        yellow = Gdk.Color.parse('yellow')[1]
        white = Gdk.Color.parse('white')[1]
        black = Gdk.Color.parse('black')[1]
        blue = Gdk.Color.parse('blue')[1]
        green = Gdk.Color.parse('green')[1]
        pink = Gdk.Color.parse(PINK)[1]
        bgcolor = Gdk.Color.parse(BACKGROUND)[1]
        darkgreen = Gdk.Color.parse(BUTTON_BACKGROUND)[1]

        # clear area
        drawgc.set_source_rgb(white.red, white.green, white.blue)
        drawgc.rectangle(0, 0, width, height)
        self.fpdraw.queue_draw()

    def selectstick(self, widget, event, data=None):
        if data:
            if self.stickselected:
                ebox = self.stickbuttons[self.stickselected]
                ebox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))
                label = ebox.get_child()
                label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_FOREGROUND))
            self.stickselected = data
            self.selectstickebox()

    def selectstickebox(self):
        ebox = self.stickbuttons[self.stickselected]
        ebox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_FOREGROUND))
        label = ebox.get_child()
        label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))

        if self.stickselected in self.key.sticks:
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
        GObject.GObject.__init__(self)

        self.playing = False
        self.playingbackwards = False
        self.toplevel = activity
        self.stickselected = 'RIGHT SHOULDER'
        self.surface = None
        self._emit_move_handle = None

        self.setplayspeed(50)

        self.keys_overlap_stack = []
        for i in range(len(model.keys)):
            self.keys_overlap_stack.append(i)

        self.key = screenflip.ScreenFrame()

        self.kfselected = 0
        self.jointpressed = None
        self.kfpressed = -1
        self.middlepressed = False
        self.rotatepressed = False
        self.iconsdir = os.path.join(get_bundle_path(), 'icons')

        # screen

        self.mfdraw = Gtk.DrawingArea()
        self.mfdraw.connect('draw', self.__draw_cb)
        self.mfdraw.connect('configure_event', self.configure_event)
        self.mfdraw.connect('motion_notify_event', self.motion_notify_event)
        self.mfdraw.connect('button_press_event', self.button_press_event)
        self.mfdraw.connect('button_release_event', self.button_release_event)
        self.mfdraw.set_events(Gdk.EventMask.EXPOSURE_MASK
                               | Gdk.EventMask.LEAVE_NOTIFY_MASK
                               | Gdk.EventMask.BUTTON_PRESS_MASK
                               | Gdk.EventMask.BUTTON_RELEASE_MASK
                               | Gdk.EventMask.POINTER_MOTION_MASK
                               | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        self.mfdraw.set_size_request(DRAWWIDTH, DRAWHEIGHT)

        screen_box = Gtk.EventBox()
        screen_box.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        screen_box.set_border_width(PAD / 2)
        screen_box.add(self.mfdraw)

        screen_pink = Gtk.EventBox()
        screen_pink.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(PINK))
        screen_pink.set_border_width(PAD)
        screen_pink.add(screen_box)

        # keyframes

        self.kfdraw = Gtk.DrawingArea()
        self.kfdraw.set_size_request(KEYFRAMEWIDTH, KEYFRAMEHEIGHT)
        self.kfdraw.connect('draw', self.__kf_draw_cb)
        self.kfdraw.connect('configure_event', self.kf_configure_event)
        self.kfdraw.connect('motion_notify_event', self.kf_motion_notify_event)
        self.kfdraw.connect('button_press_event', self.kf_button_press_event)
        self.kfdraw.connect('button_release_event', self.kf_button_release_event)
        self.kfdraw.set_events(Gdk.EventMask.EXPOSURE_MASK
                               | Gdk.EventMask.LEAVE_NOTIFY_MASK
                               | Gdk.EventMask.BUTTON_PRESS_MASK
                               | Gdk.EventMask.BUTTON_RELEASE_MASK
                               | Gdk.EventMask.POINTER_MOTION_MASK
                               | Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        kfdraw_box = Gtk.EventBox()
        kfdraw_box.set_border_width(PAD)
        kfdraw_box.add(self.kfdraw)

        # control box

        angle_box = Gtk.HBox()
        anglelabel = Gtk.Label(label=_('Angle:'))
        anglelabel.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))
        anglelabel.set_size_request(60, -1)
        angle_box.pack_start(anglelabel, False, False, 5)
        self.angleentry = Gtk.Entry()
        self.angleentry.set_max_length(3)
        self.angleentry.set_width_chars(3)
        self.angleentry.connect('activate', self.enterangle_callback, self.angleentry)
        self.angleentry.modify_bg(Gtk.StateType.INSENSITIVE,
                Gdk.color_parse(BUTTON_FOREGROUND))
        angle_box.pack_start(self.angleentry, False, False, 0)
        self.anglel_adj = Gtk.Adjustment(0, 0, 360, 1, 60, 0)
        self.anglel_adj.connect('value_changed', self._anglel_adj_cb)
        self.anglel_slider = Gtk.Scale.new(0, self.anglel_adj)
        self.anglel_slider.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            self.anglel_slider.modify_bg(state, Gdk.color_parse(color))
        angle_box.pack_start(self.anglel_slider, True, True, 0)

        size_box = Gtk.HBox()
        sizelabel = Gtk.Label(label=_('Size:'))
        sizelabel.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))
        sizelabel.set_size_request(60, -1)
        size_box.pack_start(sizelabel, False, False, 5)
        self.sizeentry = Gtk.Entry()
        self.sizeentry.set_max_length(3)
        self.sizeentry.set_width_chars(3)
        self.sizeentry.connect('activate', self.enterlen_callback, self.sizeentry)
        self.sizeentry.modify_bg(Gtk.StateType.INSENSITIVE,
                Gdk.color_parse(BUTTON_FOREGROUND))
        size_box.pack_start(self.sizeentry, False, False, 0)
        self.size_adj = Gtk.Adjustment(0, 0, 200, 1, 30, 0)
        self.size_adj.connect('value_changed', self._size_adj_cb)
        size_slider = Gtk.Scale.new(0, self.size_adj)
        size_slider.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            size_slider.modify_bg(state, Gdk.color_parse(color))
        size_box.pack_start(size_slider, True, True, 0)

        control_head_box = Gtk.VBox()
        control_head_box.pack_start(angle_box, True, True, 0)
        control_head_box.pack_start(size_box, True, True, 0)

        control_head = Gtk.EventBox()
        control_head.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_FOREGROUND))
        control_head.add(control_head_box)

        control_options = Gtk.VBox()
        self.stickbuttons = {}
        self.sticklabels = {}
        for stickpartname in LABELLIST:
            label = Gtk.Label(label=STRINGS[stickpartname])
            label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_FOREGROUND))
            self.sticklabels[stickpartname] = label
            ebox = Gtk.EventBox()
            ebox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))
            ebox.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            ebox.connect('button_press_event', self.selectstick, stickpartname)
            ebox.add(label)
            self.stickbuttons[stickpartname] = ebox
            control_options.pack_start(ebox, False, False, 0)
        self.selectstickebox()

        control_scroll = Gtk.ScrolledWindow()
        control_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        control_scroll.add_with_viewport(control_options)
        control_options.get_parent().modify_bg(Gtk.StateType.NORMAL,
                Gdk.color_parse(BUTTON_BACKGROUND))

        control_box = Gtk.VBox()
        control_box.pack_start(control_head, False, False, 0)
        control_box.pack_start(control_scroll, True, True, 0)

        control_bg = Gtk.EventBox()
        control_bg.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))
        control_bg.set_border_width(PAD / 2)
        control_bg.add(control_box)

        control_pink = Gtk.EventBox()
        control_pink.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(PINK))
        control_pink.set_border_width(PAD)
        control_pink.add(control_bg)

        # left control box

        logo = Gtk.Image()
        logo.set_from_file(os.path.join(self.iconsdir, 'logo.png'))

        leftbox = Gtk.VBox()
        leftbox.pack_start(logo, False, False, 0)
        leftbox.pack_start(control_pink, True, True, 0)

        # desktop

        hdesktop = Gtk.HBox()
        hdesktop.pack_start(leftbox, False, False, 0)
        hdesktop.pack_start(screen_pink, False, False, 0)

        desktop = Gtk.VBox()
        desktop.pack_start(hdesktop, True, True, 0)
        desktop.pack_start(kfdraw_box, False, False, 0)

        greenbox = Gtk.EventBox()
        greenbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(PAD / 2)
        greenbox.add(desktop)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(YELLOW))
        self.add(greenbox)
        self.show_all()

    def _draw_frame(self, index, surface):
        joints = self.frames[index].joints
        parts = self.frames[index].parts
        # draw on the main drawing area
        area = self.toplevel.get_window()
        drawgc = cairo.Context(surface)
        drawgc.set_line_width(3)
        white = Gdk.Color.parse('white')
        black = Gdk.Color.parse('black')
        width = self.mfdraw.get_allocated_width()
        height = self.mfdraw.get_allocated_height()
        #pixmap = Gdk.Pixmap(self.mfdraw.window, width, height)
        # clear area
        drawgc.set_source_rgb(0, 0, 0)
        drawgc.rectangle(0, 0, width, height)
        drawgc.fill()

        drawgc.set_source_rgb(1, 1, 1)
        hsize = self.frames[index].hsize
        middle = self.frames[index].middle
        rhsize = parts['RIGHT HAND']
        lhsize = parts['LEFT HAND']
        self.drawstickman(drawgc, surface, middle, joints, hsize, rhsize, lhsize)

    def _inkeyframe(self, x, y):
        dy = math.pow(abs(y - KEYFRAMEHEIGHT / 2), 2)

        for i, key in enumerate(self.keys_overlap_stack):
            dx = math.pow(abs(x - model.keys[key].x), 2)
            l = math.sqrt(dx + dy)
            if int(l) <= KEYFRAME_RADIUS:
                self.keys_overlap_stack.pop(i)
                self.keys_overlap_stack.insert(0, key)
                return key

        return -1

    def _anglel_adj_cb(self, adj):
        self.angleentry.set_text(str(int(adj.get_value())))
        self.enterangle_callback(None, self.angleentry)

    def _size_adj_cb(self, adj):
        self.sizeentry.set_text(str(int(adj.get_value())))
        self.enterlen_callback(None, self.sizeentry)

    def _emit_move(self, key):
        self._emit_move_handle = None
        self.emit('frame-changed', key)
        return False


def _inarea(widget, x, y):
    width = widget.get_allocated_width()
    height = widget.get_allocated_height()
    if x < 0 or y < 0 or x >= width or y >= height:
        return False
    return True
