# -*- coding: utf-8 -*-
# from anz.casclient.casclient import manage_addAnzCASClient
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

from genweb6.upc.cas.interface import ICASSettings


def setupCASUPC(context):
    portal = context.getSite()

    # Try to delete a possible existing instance of CASUPC object.
    try:
        portal.acl_users.manage_delObjects('CASUPC')
    except:
        pass

    try:
        # TODO Comentado porque no funciona el paquete de anz.casclient
        # manage_addAnzCASClient(portal.acl_users, "CASUPC", title="CASUPC")
        portal.acl_users.CASUPC.casServerUrlPrefix = 'https://sso.upc.edu/CAS/'
        # portal.acl_users.CASUPC.gateway = True
        portal.acl_users.CASUPC.ticketValidationSpecification = 'CAS 2.0'
        plugin = portal.acl_users['CASUPC']
        plugin.manage_activateInterfaces(['IAuthenticationPlugin', 'IChallengePlugin', 'IExtractionPlugin'])
    except:
        pass

    # Try to migrate the existing App descriptor for CAS login page.
    try:
        genweb_props = api.portal.get_tool(name='portal_properties').genwebupc_properties
        registry = queryUtility(IRegistry)
        cas_settings = registry.forInterface(ICASSettings)
        cas_settings.cas_app_name = genweb_props.CASAuthAppName
    except:
        pass
