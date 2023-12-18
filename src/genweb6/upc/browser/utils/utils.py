# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection

from genweb6.core.controlpanels.footer import IFooterSettings
from genweb6.core.utils import json_response
from genweb6.upc.controlpanels.upc import IUPCSettings

# try:
#     from genweb6.serveistic.controlpanels.facetes import IServeisTICFacetesControlPanelSettings
#     HAS_TFEMARKET = True
# except:
#     HAS_TFEMARKET = False

# try:
#     from genweb6.tfemarket.controlpanels.tfemarket import ITfemarketSettings
#     HAS_SERVEISTIC = True
# except:
#     HAS_SERVEISTIC = False


class UtilsView(BrowserView):
    pass


# TODO Terminar de hacer
class get_controlpanels_settings(BrowserView):
#     """
# Retorna tota la informació del controlpanel
#     """

    @json_response
    def __call__(self):
        settings = {}
        registry = getUtility(IRegistry)

        # genweb6.core.controlpanels.footer.IFooterSettings
        try:
            footer_settings = registry.forInterface(IFooterSettings)
            FOOTER_ID = 'genweb6.core.controlpanels.footer.IFooterSettings'
            settings.update({FOOTER_ID: {}})

            try:
                settings[FOOTER_ID].update({'table_links_ca': footer_settings.table_links_ca})
            except:
                settings[FOOTER_ID].update({'error_table_links_ca': None})

            try:
                settings[FOOTER_ID].update({'table_links_es': footer_settings.table_links_es})
            except:
                settings[FOOTER_ID].update({'error_table_links_es': None})

            try:
                settings[FOOTER_ID].update({'table_links_en': footer_settings.table_links_en})
            except:
                settings[FOOTER_ID].update({'error_table_links_en': None})
        except:
            settings.update({'error_' + FOOTER_ID: None})

        # genweb6.upc.controlpanels.upc.IUPCSettings
        try:
            upc_settings = registry.forInterface(IUPCSettings)
            UPC_ID = 'genweb6.upc.controlpanels.upc.IUPCSettings'
            settings.update({UPC_ID: {}})

            try:
                settings[UPC_ID].update({'xarxes_socials': upc_settings.xarxes_socials})
            except:
                settings[UPC_ID].update({'error_xarxes_socials': None})

            try:
                settings[UPC_ID].update({'contact_emails_table': upc_settings.contact_emails_table})
            except:
                settings[UPC_ID].update({'error_contact_emails_table': None})
        except:
            settings.update({'error_' + UPC_ID: None})

        return settings

class fix_record_upc(BrowserView):
    """
Soluciona el problema de KeyError quan la plonesite es mou del Zeo original
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        output = []
        site = self.context.portal_registry
        registry = getUtility(IRegistry)
        rec = registry.records
        keys = [a for a in rec.keys()]
        for k in keys:
            try:
                rec[k]
            except:
                output.append('{}, '.format(k))
                output.append('{}, '.format(site.portal_registry.records._values[k]))
                del site.portal_registry.records._values[k]
                del site.portal_registry.records._fields[k]
        return "S'han purgat les entrades del registre: {}".format(output)