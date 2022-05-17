# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface

from genweb6.upc import _


class ICASSettings(Interface):
    """ Global CAS settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    cas_app_name = schema.TextLine(
        title=_(u"cas_app_name",
                default=u"Desciptor de l'aplicació"),
        description=_(u"help_cas_app_name",
                      default=u"El descriptor per la personalització de l'aplicació per la pantalla de login de CAS"),
        required=False,
        default=u"genweb",
    )
