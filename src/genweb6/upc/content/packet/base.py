# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations

from genweb6.upc.content.packet import PACKETS_KEY


class BasePacket(object):
    """ The default packet boilerplate """

    def get_packet_fields(self):
        annotations = IAnnotations(self.context)
        self._packet_fields = annotations.setdefault(PACKETS_KEY + '.fields', PersistentDict(self.default))
        return self._packet_fields

    def set_packet_fields(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY + '.fields', PersistentDict(self.default))
        annotations[PACKETS_KEY + '.fields'] = value

    packet_fields = property(get_packet_fields, set_packet_fields)

    def get_packet_type(self):
        annotations = IAnnotations(self.context)
        self._type = annotations.setdefault(PACKETS_KEY + '.type', '')
        return self._type

    def set_packet_type(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY + '.type', '')
        annotations[PACKETS_KEY + '.type'] = value

    packet_type = property(get_packet_type, set_packet_type)

    def get_mapui(self):
        annotations = IAnnotations(self.context)
        self._mapui = annotations.setdefault(PACKETS_KEY + '.mapui', '')
        return self._mapui

    def set_mapui(self, value):
        annotations = IAnnotations(self.context)
        annotations.setdefault(PACKETS_KEY + '.mapui', '')
        annotations[PACKETS_KEY + '.mapui'] = value

    packet_mapui = property(get_mapui, set_mapui)
