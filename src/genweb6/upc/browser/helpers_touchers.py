from Products.Five.browser import BrowserView
import transaction
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.ramcache import ram
from genweb6.core.controlpanels.header import IHeaderSettings
from genweb6.core.purge import purge_varnish_paths
from genweb6.upc.controlpanels.upc import registerMissingUPCRecords
from genweb6.upc.utils import genwebUPCConfig
from genweb6.upc.utils import validateGoogleMapsAPIKey

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


class setup_google_maps_apikey(BrowserView):
    """
Definir l'API Key de Google Maps del controlpanel de Contacte

Paràmetres:
- api_key: API Key de Google Cloud amb la Maps Embed API habilitada (buit per esborrar-la)

Abans de desar-la es comprova contra Google amb la URL de la web com a referer.
    """

    def __call__(self):
        if 'api_key' not in self.request.form:
            return 'KO: falta el paràmetre api_key'

        api_key = self.request.form['api_key'].strip() or None
        if api_key:
            valid = validateGoogleMapsAPIKey(api_key, self.context.absolute_url() + '/')
            if valid is False:
                return 'KO: API Key no vàlida o no autoritzada per a aquest domini'

        registerMissingUPCRecords()
        genwebUPCConfig().google_maps_api_key = api_key

        transaction.commit()

        ram.caches.clear()
        purge_varnish_paths(self, ['/_purge_all'])

        return 'OK'
