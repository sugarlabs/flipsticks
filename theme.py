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

FPWIDTH = 150
FPHEIGHT = 100
#DRAWHEIGHT = 300 for my laptop
KEYFRAMEWIDTH = gtk.gdk.screen_width() - 406 # 675
KEYFRAMEHEIGHT = 80
DRAWWIDTH = KEYFRAMEWIDTH + 64 # 750
DRAWHEIGHT = gtk.gdk.screen_height() - 370 # 500

KEYFRAMES = [] # [50,190,337,487,625]
TOTALFRAMES = 30

for i in range(5):
    keyframe_width  = KEYFRAMEWIDTH/5
    KEYFRAMES.append(keyframe_width/2 + i*keyframe_width)

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
