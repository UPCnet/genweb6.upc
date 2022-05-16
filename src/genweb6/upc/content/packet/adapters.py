# -*- coding: utf-8 -*-
from zope.component import adapts
from zope.interface import implementer

from genweb6.upc import _
from genweb6.upc.content.packet.base import BasePacket
from genweb6.upc.content.packet.packet import Ipacket
from genweb6.upc.content.packet.packet import IpacketDefinition


@implementer(IpacketDefinition)
class FitxaGrau(BasePacket):
    adapts(Ipacket)

    order = 1

    def __init__(self, context):
        self.context = context
        self.title = _(u"Fitxa de grau")
        self.description = _(u"Informació sobre un estudi d'un grau específic")
        self.URL_schema = 'http://www.upc.edu/grau/fitxa_grau.php?codi=%(codi_grau)s&lang=%(lang)s&sense_titol&contingut_upc=true'
        self.fields = [_(u'codi_grau')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'codi_grau')


@implementer(IpacketDefinition)
class PlaEstudisGrau(BasePacket):
    adapts(Ipacket)

    order = 2

    def __init__(self, context):
        self.context = context
        self.title = _(u"Pla d'estudi de grau")
        self.description = _(u"Informació sobre el pla d'estudis d'un grau específic")
        self.URL_schema = 'http://www.upc.edu/grau/fitxa_grau.php?codi=%(codi_grau)s&lang=%(lang)s&pla_estudis&sense_titol&contingut_upc=true'
        self.fields = [_(u'codi_grau')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'codi_grau')


@implementer(IpacketDefinition)
class FitxaMaster(BasePacket):
    adapts(Ipacket)

    order = 3

    # http://www.upc.edu/master/fitxa_master.php?id_estudi=19&lang=ca
    def __init__(self, context):
        self.context = context

        self.title = _(u"Fitxa de màster")
        self.description = _(u"Informació sobre un màster específic")
        self.URL_schema = 'http://www.upc.edu/master/fitxa_master.php?id_estudi=%(codi_master)s&lang=%(lang)s&sense_titol&contingut_upc=true'
        self.fields = [_(u'codi_master')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'codi_master')


@implementer(IpacketDefinition)
class PlaEstudisMaster(BasePacket):
    adapts(Ipacket)

    order = 4

    # http://www.upc.edu/master/fitxa_master.php?id_estudi=19&lang=ca
    def __init__(self, context):
        self.context = context

        self.title = _(u"Pla d'estudis de màster")
        self.description = _(u"Informació sobre un pla d'estudis de màster específic")
        self.URL_schema = 'http://www.upc.edu/master/fitxa_master.php?id_estudi=%(codi_pla_master)s&lang=%(lang)s&pla_estudis&sense_titol&contingut_upc=true'
        self.fields = [_(u'codi_pla_master')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'codi_pla_master')


@implementer(IpacketDefinition)
class GrupsRecercaDepartament(BasePacket):
    adapts(Ipacket)

    order = 5

    def __init__(self, context):
        self.context = context
        self.title = _(u"Grups de recerca")
        self.description = _(u"Grups de recerca d'un departament específic")
        self.URL_schema = 'http://www.upc.edu/ws/drac/LlistatGrupsRecercav1.php?codiupc=%(codi_departament)s&lang=%(lang)s&contingut_upc=true'
        self.fields = [_(u'codi_departament')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'codi_departament')


@implementer(IpacketDefinition)
class InvestigadorsGrupRecercaDepartament(BasePacket):
    adapts(Ipacket)

    order = 6

    def __init__(self, context):
        self.context = context
        self.title = _(u"Investigadors d'un grup de recerca")
        self.description = _(u"Investigadors d'un grup de recerca d'un departament específic")
        self.URL_schema = 'http://www.upc.edu/ws/drac/LlistatInvestigadorsGRv1.php?acronim=%(acronim)s&lang=%(lang)s&contingut_upc=true'
        self.fields = [_(u'acronim')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'acronim')


@implementer(IpacketDefinition)
class ContingutGenweb(BasePacket):
    adapts(Ipacket)

    order = 7

    def __init__(self, context):
        self.context = context
        self.title = _(u"Contingut existent")
        self.description = _(u"Contingut d'una pàgina externa")
        self.URL_schema = '%(url_contingut)s'
        self.fields = [_(u'url_contingut'), _(u'element')]
        self.default = dict([(field, '') for field in self.fields])
        self.mapui = dict(codi=u'url_contingut', element=u'element')
