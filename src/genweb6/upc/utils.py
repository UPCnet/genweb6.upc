# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from time import time
from urllib.parse import quote
from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory

from genweb6.upc.controlpanels.bus_soa import IBusSOASettings
from genweb6.upc.controlpanels.identitat_digital import IIdentitatDigitalSettings
from genweb6.upc.controlpanels.upc import IUPCSettings

import logging
import requests

logger = logging.getLogger(__name__)

PLMF = MessageFactory('plonelocales')


def _contact_ws_cachekey(method, self, unitat):
    """Cache by the unitat value"""
    return (unitat)


@ram.cache(lambda *args: time() // (24 * 60 * 60))
def genwebBusSOAConfig():
    registry = queryUtility(IRegistry)
    return registry.forInterface(IBusSOASettings)


@ram.cache(lambda *args: time() // (24 * 60 * 60))
def genwebIdentitatDigitalConfig():
    registry = queryUtility(IRegistry)
    return registry.forInterface(IIdentitatDigitalSettings)


#@ram.cache(lambda *args: time() // (24 * 60 * 60))
def genwebUPCConfig():
    registry = queryUtility(IRegistry)
    # check=False: les webs sense l'upgrade aplicat no tenen tots els camps al registre
    return registry.forInterface(IUPCSettings, check=False)


def validateGoogleMapsAPIKey(api_key, referer):
    """ Comprova l'API Key contra la Maps Embed API enviant com a referer la URL de la web.
        Retorna True si és vàlida, False si Google la rebutja i None si no s'ha pogut comprovar.
    """
    try:
        r = requests.get('https://www.google.com/maps/embed/v1/place',
                         params={'key': api_key, 'q': 'UPC'},
                         headers={'Referer': referer},
                         timeout=10)
    except Exception:
        logger.warning('No s\'ha pogut validar l\'API Key de Google Maps')
        return None

    if r.status_code == 200:
        return True
    if 400 <= r.status_code < 500:
        return False
    return None


class genwebUPCUtils(BrowserView):
    """ Convenience methods placeholder genweb.utils view. """

    def genwebBusSOAConfig(self):
        return genwebBusSOAConfig()

    def genwebIdentitatDigitalConfig(self):
        return genwebIdentitatDigitalConfig()

    def genwebUPCConfig(self):
        return genwebUPCConfig()

    @ram.cache(_contact_ws_cachekey)
    def _queryInfoUnitatWS(self, unitat):
        try:
            r = requests.get('https://bus-soa.upc.edu/SCP/InfoUnitatv1?id=%s' % unitat, timeout=10)
            return r.json()
        except:
            return False

    def getDadesUnitat(self):
        """ Retorna les dades proporcionades pel WebService del SCP """
        config = self.genwebUPCConfig()
        unitat = config.contacte_id
        if unitat:
            dades = self._queryInfoUnitatWS(unitat)
            if not dades or 'error' in dades:
                return False
            else:
                lang = self.context.Language()
                if not lang:
                    lang = 'ca'

                if config.custom_map_address and config.custom_map_address != "":
                    dades['google_maps'] = self.getGoogleMapsURL(config.custom_map_address, lang)
                else:
                    dades['google_maps'] = self.getGoogleMapsURL(dades.get('adreça', ''), lang)

                return dades
        else:
            return False

    def getGoogleMapsURL(self, address, lang=None):
        if not lang:
            lang = self.context.Language()
            if not lang:
                lang = 'ca'

        api_key = self.genwebUPCConfig().google_maps_api_key
        if api_key:
            return "https://www.google.com/maps/embed/v1/place?" + \
                "key=" + quote(api_key) + \
                "&q=" + quote(address) + \
                "&language=" + lang

        # Format antic sense API Key
        return "https://maps.google.com/maps?" + \
            "width=100%" + \
            "&height=300" + \
            "&hl=" + lang + \
            "&q=" + address.replace(' ', '%20') + "+()" + \
            "&t=" + \
            "&z=15" + \
            "&ie=UTF8" + \
            "&iwloc=B" + \
            "&output=embed"

    def getDadesContact(self):
        """ Retorna les dades proporcionades pel WebService del SCP
            per al contacte
        """
        dades = self.getDadesUnitat()
        if dades:
            idioma = self.context.Language()
            if not idioma:
                idioma = "ca"

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
                    'google_maps': dades.get('google_maps', ''),
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
                    'google_maps': dades.get('google_maps', ''),
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
                    'google_maps': dades.get('google_maps', ''),
                }
            }
            return dict_contact[idioma]
        else:
            return ""


def getTokenIdentitatDigital():
    identitat_digital_tool = genwebIdentitatDigitalConfig()
    urlGetToken = identitat_digital_tool.identitat_url + '/gcontrol/rest/acls/processos?idProces='
    idProces = identitat_digital_tool.identitat_apikey
    return requests.post(urlGetToken + idProces)
