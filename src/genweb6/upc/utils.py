# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from zope.i18nmessageid import MessageFactory
from zope.component import queryUtility

from genweb6.upc.controlpanel import IUPCSettings

import logging
import requests

logger = logging.getLogger(__name__)

PLMF = MessageFactory('plonelocales')


def _contact_ws_cachekey(method, self, unitat):
    """Cache by the unitat value"""
    return (unitat)


class genwebUPCUtils(BrowserView):
    """ Convenience methods placeholder genweb.utils view. """

    def genwebUPCConfig(self):
        """ Funcio que retorna les configuracions del controlpanel """
        registry = queryUtility(IRegistry)
        return registry.forInterface(IUPCSettings)

    @ram.cache(_contact_ws_cachekey)
    def _queryInfoUnitatWS(self, unitat):
        try:
            r = requests.get(
                'https://bus-soa.upc.edu/SCP/InfoUnitatv1?id=%s' % unitat, timeout=10)
            return r.json()
        except:
            return {}

    def getDadesUnitat(self):
        """ Retorna les dades proporcionades pel WebService del SCP """
        unitat = self.genwebUPCConfig().contacte_id
        if unitat:
            dades = self._queryInfoUnitatWS(unitat)
            if 'error' in dades:
                return False
            else:
                return dades
        else:
            return False

    def getDadesContact(self):
        """ Retorna les dades proporcionades pel WebService del SCP
            per al contacte
        """
        dades = self.getDadesUnitat()
        if dades:
            idioma = self.context.Language()
            dict_contact = {
                'ca': {
                    'adreca_sencera': ((dades.get('campus_ca', '') and
                                        dades.get('campus_ca') + ', ') +
                                        dades.get('edifici_ca', '') + '. ' +
                                        dades.get('adreca', '') + ' ' +
                                        dades.get('codi_postal', '') + ' ' +
                                        dades.get('localitat', '')),
                    'nom': dades.get('nom_ca', ''),
                    'telefon': dades.get('telefon', ''),
                    'fax': dades.get('fax', ''),
                    'email': dades.get('email', ''),
                    'id_scp': dades.get('id', ''),
                    'codi_upc': dades.get('codi_upc', ''),
                },
                'es': {
                    'adreca_sencera': ((dades.get('campus_es', '') and
                                        dades.get('campus_es') + ', ') +
                                        dades.get('edifici_es', '') + '. ' +
                                        dades.get('adreca', '') + ' ' +
                                        dades.get('codi_postal', '') + ' ' +
                                        dades.get('localitat', '')),
                    'nom': dades.get('nom_es', ''),
                    'telefon': dades.get('telefon', ''),
                    'fax': dades.get('fax', ''),
                    'email': dades.get('email', ''),
                    'id_scp': dades.get('id', ''),
                    'codi_upc': dades.get('codi_upc', ''),
                },
                'en': {
                    'adreca_sencera': ((dades.get('campus_en', '') and
                                        dades.get('campus_en') + ', ') +
                                        dades.get('edifici_en', '') + '. ' +
                                        dades.get('adreca', '') + ' ' +
                                        dades.get('codi_postal', '') + ' ' +
                                        dades.get('localitat', '')),
                    'nom': dades.get('nom_en', ''),
                    'telefon': dades.get('telefon', ''),
                    'fax': dades.get('fax', ''),
                    'email': dades.get('email', ''),
                    'id_scp': dades.get('id', ''),
                    'codi_upc': dades.get('codi_upc', ''),
                }
            }
            return dict_contact[idioma]
        else:
            return ""
