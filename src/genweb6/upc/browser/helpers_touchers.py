from Products.Five.browser import BrowserView
import transaction
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from genweb6.core.controlpanels.header import IHeaderSettings

class setup_header_languages(BrowserView):
    def __call__(self):
        registry = getUtility(IRegistry)
        
        header_settings = registry.forInterface(IHeaderSettings)

        header_settings.logo_alt_es = "Universitat Politècnica de Catalunya"
        header_settings.logo_alt_en = "Universitat Politècnica de Catalunya"
        header_settings.logo_url_es = "https://www.upc.edu/es"
        header_settings.logo_url_en = "https://www.upc.edu/en"


        transaction.commit()
        
        return 'Done'
