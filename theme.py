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

import gtk
from gettext import gettext as _

from sugar.graphics import style

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

STRINGS = { 'size'              : _('Size'),
            'angle'             : _('Angle'),
            'lessonplan'        : _('Lesson Plans'),
            'lpdir'             : _('lp-en'),
            'export'            : _('Export Frame One'),
            'HEAD'              : _('Head'),
            'NECK'              : _('Neck'),
            'RIGHT SHOULDER'    : _('Right Shoulder'),
            'UPPER RIGHT ARM'   : _('Upper Right Arm'),
            'LOWER RIGHT ARM'   : _('Lower Right Arm'),
            'RIGHT HAND'        : _('Right Hand'),
            'LEFT SHOULDER'     : _('Left Shoulder'),
            'UPPER LEFT ARM'    : _('Upper Left Arm'),
            'LOWER LEFT ARM'    : _('Lower Left Arm'),
            'LEFT HAND'         : _('Left Hand'),
            'TORSO'             : _('Torso'),
            'RIGHT HIP'         : _('Right Hip'),
            'UPPER RIGHT LEG'   : _('Upper Right Leg'),
            'LOWER RIGHT LEG'   : _('Lower Right Leg'),
            'RIGHT FOOT'        : _('Right Foot'),
            'LEFT HIP'          : _('Left Hip'),
            'UPPER LEFT LEG'    : _('Upper Left Leg'),
            'LOWER LEFT LEG'    : _('Lower Left Leg'),
            'LEFT FOOT'         : _('Left Foot') }

PAD = 10
LOGO_WIDTH = 276
TOLLBAR_HEIGHT = style.LARGE_ICON_SIZE

KEYFRAMEWIDTH = gtk.gdk.screen_width() - PAD*3
KEYFRAMEHEIGHT = 80

DRAWWIDTH = gtk.gdk.screen_width() - LOGO_WIDTH - PAD*4
DRAWHEIGHT = gtk.gdk.screen_height() - KEYFRAMEHEIGHT - PAD*6 - TOLLBAR_HEIGHT

KEYFRAMES = []
KEYFRAMES_NUMBER = 5
TOTALFRAMES = 30

KEYFRAME_RADIUS = 40

MOVEMIT_TIMEOUT = 1000

for i in range(KEYFRAMES_NUMBER):
    keyframe_width  = KEYFRAMEWIDTH/KEYFRAMES_NUMBER
    KEYFRAMES.append(keyframe_width/2 + i*keyframe_width)

# scale coordinates between native resolution and transportable

TRANSFER_DRAWWIDTH = 350
TRANSFER_DRAWHEIGHT = 350
TRANSFER_KEYFRAMEWIDTH = 600

def scale_keyframe(x):
    factor = float(TRANSFER_KEYFRAMEWIDTH) / (KEYFRAMEWIDTH)
    x = max(KEYFRAME_RADIUS, int(x/factor))
    x = min(KEYFRAMEWIDTH-KEYFRAME_RADIUS-1, x)
    return x

def scale_middle(middle):
    if not middle:
        return None
    x_factor = float(TRANSFER_DRAWWIDTH) / DRAWWIDTH
    y_factor = float(TRANSFER_DRAWHEIGHT) / DRAWHEIGHT
    return (min(DRAWWIDTH-1, int(middle[0]/x_factor)),
            min(DRAWHEIGHT-1, int(middle[1]/y_factor)))

def unscale_keyframe(x):
    factor = float(TRANSFER_KEYFRAMEWIDTH) / (KEYFRAMEWIDTH)
    return int(x*factor)

def unscale_middle(middle):
    if not middle:
        return None
    x_factor = float(TRANSFER_DRAWWIDTH) / DRAWWIDTH
    y_factor = float(TRANSFER_DRAWHEIGHT) / DRAWHEIGHT
    return (int(middle[0]*x_factor), int(middle[1]*y_factor))

# defaults

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
