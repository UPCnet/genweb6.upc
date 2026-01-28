# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import ISiteSchema

from plone.formwidget.namedfile.converter import b64encode_file
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.ramcache import ram

from genweb6.core.browser.helpers.helpers_ldap import setSetupLDAPUPC
from genweb6.core.cas.controlpanel import setupCAS
from genweb6.core.controlpanels.header import IHeaderSettings
from genweb6.core.controlpanels.login import ILoginSettings
from genweb6.core.controlpanels.netejar_metadades import IMetadadesSettings

import os
import pkg_resources
import transaction


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "genweb6.upc:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["genweb6.upc.upgrades"]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    portal = getSite()

    # # Uninstall CAS settings
    # cas_settings = getCASSettings()
    # cas_settings.enabled = False
    # cas_settings.login_text_btn = ""
    #
    # # Uninstall LDAP UPC
    # if getattr(portal.acl_users, 'ldapUPC', None):
    #     portal.acl_users.manage_delObjects('ldapUPC')
    #
    # # Unsetup change password setting
    # login_settings = genwebLoginConfig()
    # login_settings.change_password_url = ""
    #
    # # Unsetup logo
    # header_settings = genwebHeaderConfig()
    # header_settings.logo = None
    # header_settings.logo_responsive = None
    # header_settings.logo_alt = ""
    # header_settings.logo_url = ""
    # header_settings.logo_external_url = False
    #
    # # Unsetup favicon
    # registry = getUtility(IRegistry)
    # settings = registry.forInterface(ISiteSchema, prefix="plone")
    # settings.site_favicon = None


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('genweb6.upc_various.txt') is None:
        return

    egglocation = pkg_resources.get_distribution('genweb6.upc').location

    # Setup CAS settings
    setupCAS("https://login.upc.edu/realms/upc/protocol/cas/", "genweb", "UPC")

    url = getRequest().URL
    if url and any(x in url for x in ['fepre.upc.edu', '.pre.upc.edu']):
        setupCAS("https://login.pre.upc.edu/realms/upc/protocol/cas/", "genweb", "UPC")

    # Setup LDAP UPC
    setSetupLDAPUPC()

    # Setup change password setting
    ram.caches.clear()

    registry = getUtility(IRegistry)
    login_settings = registry.forInterface(ILoginSettings)

    if not login_settings.change_password_url:
        login_settings.change_password_url = "http://www.upcnet.es/CanviContrasenyaUPC"

    # Setup logo
    header_settings = registry.forInterface(IHeaderSettings)

    if not header_settings.logo:
        logo = open('{}/genweb6/upc/theme/img/logo.png'.format(egglocation), 'rb').read()
        encoded_data = b64encode_file(filename='logo.png', data=logo)
        header_settings.logo = encoded_data

        header_settings.logo_alt = "Universitat Politècnica de Catalunya"
        header_settings.logo_alt_es = "Universitat Politècnica de Catalunya"
        header_settings.logo_alt_en = "Universitat Politècnica de Catalunya"
        header_settings.logo_url = "https://www.upc.edu/ca"
        header_settings.logo_url_es = "https://www.upc.edu/es"
        header_settings.logo_url_en = "https://www.upc.edu/en"
        header_settings.logo_external_url = True

    # Setup favicon
    settings = registry.forInterface(ISiteSchema, prefix="plone")
    if not settings.site_favicon:
        favicon = open('{}/genweb6/upc/theme/img/favicon.ico'.format(egglocation), 'rb').read()
        encoded_data = b64encode_file(filename='favicon.ico', data=favicon)
        settings.site_favicon = encoded_data

    metadades_settings = registry.forInterface(IMetadadesSettings)
    metadades_servei_apikey = os.environ.get("metadades_servei_apikey", "")
    if not metadades_settings.api_url and metadades_servei_apikey:
        metadades_settings.api_url = "https://utilitatspdf.upc.edu/api/netejaMetadadesPDF"
        metadades_settings.api_key = metadades_servei_apikey

    metadades_indicadors_apikey = os.environ.get("metadades_indicadors_apikey", "")
    if not metadades_settings.indicadors_api_url and metadades_indicadors_apikey:
        metadades_settings.indicadors_api_url = "https://indicadorstic.upc.edu/indicadorstic/"
        metadades_settings.indicadors_api_key = metadades_indicadors_apikey
        metadades_settings.indicadors_servei_id = "NetejaMetadades"
        metadades_settings.indicadors_categoria_id = "indicadorMetadades"

    transaction.commit()