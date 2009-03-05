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

import dbus
import pickle
import logging
from dbus.gobject_service import ExportedGObject
from dbus.service import method, signal

try:
    import json
    json.dumps
except (ImportError, AttributeError):
    import simplejson as json

from sugar.presence import presenceservice

import model

logger = logging.getLogger('flipsticks')

SERVICE = 'org.freedesktop.Telepathy.Tube.Connect'
IFACE = SERVICE
PATH = '/org/freedesktop/Telepathy/Tube/Connect'

class Slot:
    def __init__(self, seqno=-1, owner=None):
        self.seqno = seqno
        self.owner = owner

class Messenger(ExportedGObject):
    def __init__(self, tube, initiator, view):
        ExportedGObject.__init__(self, tube, PATH)

        self.initiator = initiator
        self._tube = tube
        self._entered = False
        self._slots = []
        self._view = view

        self._view.connect('frame-changed', self._frame_changed_cb)
        self._tube.watch_participants(self._participant_change_cb)

    def _participant_change_cb(self, added, removed):
        if not self._entered and added:
            self.me = self._tube.get_unique_name()

            for i in range(len(model.keys)):
                self._slots.append(Slot())

            if self.initiator:
                self._tube.add_signal_receiver(self._ping_cb, '_ping', IFACE,
                        path=PATH, sender_keyword='sender')
                for i in self._slots:
                    i.seqno = 0
                    i.owner = self.me
            else:
                self._pong_handle = self._tube.add_signal_receiver(
                        self._pong_cb, '_pong', IFACE, path=PATH,
                        sender_keyword='sender')
                self._ping()

            self._tube.add_signal_receiver(self._notify_cb, '_notify', IFACE,
                    path=PATH, sender_keyword='sender')
            self._entered = True

    # incomers' signal to retrieve initial snapshot
    @signal(IFACE, signature='')
    def _ping(self):
        logger.debug('send ping')
        pass

    # object is ready to post snapshot to incomer
    @signal(IFACE, signature='')
    def _pong(self):
        logger.debug('send pong')
        pass

    # slot was changed
    @signal(IFACE, signature='iiss')
    def _notify(self, slot, seqno, sender, raw):
        pass

    # the whole list of slots for incomers
    @method(dbus_interface=IFACE, in_signature='', out_signature='a(iss)',
            sender_keyword='sender')
    def _snapshot(self, sender=None):
        logger.debug('_snapshot requested from %s' % sender)
        out = []

        for i, slot in enumerate(self._slots):
            out.append((slot.seqno, slot.owner,
                    json.dumps(model.keys[i].collect())))

        return out

    def _ping_cb(self, sender=None):
        if sender == self.me:
            return
        logger.debug('_ping received from %s' % sender)
        self._pong()

    def _pong_cb(self, sender=None):
        if sender == self.me:
            return
        logger.debug('_pong sent from %s' % sender)

        # we've got source for _snapshot and don't need _pong anymore
        self._tube.remove_signal_receiver(self._pong_handle)
        self._pong_handle = None

        remote = self._tube.get_object(sender, PATH)
        rawlist = remote._snapshot()

        logger.debug('snapshot received len=%d' % len(rawlist))

        for i, (seqno, owner, raw) in enumerate(rawlist):
            self._receive(i, seqno, owner, raw, sender)

        # we are ready to receive _snapshot requests
        self._tube.add_signal_receiver(self._ping_cb, '_ping', IFACE,
                path=PATH, sender_keyword='sender')

    def _notify_cb(self, slot, seqno, owner, raw, sender=None):
        if sender == self.me:
            return
        logger.debug('_notify requested from %s' % sender)
        self._receive(slot, seqno, owner, raw, sender)

    def _receive(self, slot, seqno, owner, raw, sender):
        cur = self._slots[slot]
        new = Slot(seqno, owner)

        logger.debug('object received slot=%s seqno=%d owner=%s from %s'
                % (slot, new.seqno, new.owner, sender))

        if cur.seqno > new.seqno:
            logger.debug('trying to rewrite newer value by older one')
            return
        elif cur.seqno == new.seqno:
            # arrived value was sent at the same time as current one
            if cur.owner > new.owner:
                logger.debug('current value is higher ranked then arrived')
                return
            if cur.owner == self.me:
                # we sent current and arrived value rewrites it
                logger.debug('resend current with higher seqno')
                self._send(slot)
                return
            else:
                logger.debug('just discard low rank')
                return
        else:
            logger.debug('accept higher seqno')

        self._view.props.keyframe = (slot, model.StoredFrame(json.loads(raw)))
        self._slots[slot] = new

    def _send(self, slot_num):
        slot = self._slots[slot_num]
        slot.seqno += 1
        slot.owner = self.me

        self._notify(slot_num, slot.seqno, slot.owner,
                json.dumps(model.keys[slot_num].collect()))

        logger.debug('_send slot=%s seqno=%d' % (slot_num, slot.seqno))

    def _frame_changed_cb(self, sender, slot):
        self._send(slot)
