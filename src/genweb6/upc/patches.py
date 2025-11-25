from Acquisition import aq_inner
from Products.CMFPlone.PloneTool import CEILING_DATE
from Products.CMFPlone.PloneTool import FLOOR_DATE
from Products.CMFPlone.PloneTool import METADATA_DC_AUTHORFIELDS
from Products.CMFPlone.PloneTool import METADATA_DCNAME
from AccessControl import ClassSecurityInfo
import re
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.base.utils import safe_text
from plone.base.interfaces import ISiteSchema
from plone.base.interfaces import ISecuritySchema
from DateTime import DateTime
from urllib.parse import urlparse

import logging
import os

logger = logging.getLogger('plone.cachepurging')

# Desactivado porque no se usa creo que se usaba para purgar varnish en GW4 y ahora lo hacemos con varnish
# def purge(self, session, url, httpVerb="PURGE"):
#     """Perform the single purge request.

#     Returns a triple ``(resp, xcache, xerror)`` where ``resp`` is the
#     response object for the connection, ``xcache`` is the contents of the
#     X-Cache header, and ``xerror`` is the contents of the first header
#     found of the header list in ``self.errorHeaders``.
#     """
#     __traceback_info__ = url
#     logger.debug("making %s request to %s", httpVerb, url)
#     resp = session.request(httpVerb, url, timeout=self.timeout)
#     xcache = resp.headers.get("x-cache", "")
#     xerror = ""
#     ZOPE_HOME = os.environ['PWD']
#     (scheme, host, path, params, query, fragment) = urlparse(url)
#     try:
#         f = open(ZOPE_HOME + '/var/log/urls_to_purge', 'a')
#         f.write(path + '\n')
#         f.close()
#     except IOError:
#         logger.warning('Can not write to urls_to_purge file on %s/var/log', ZOPE_HOME)
#     except KeyError:
#         logger.warning('No env variable called ZOPE_HOME')
#     for header in self.errorHeaders:
#         xerror = resp.headers.get(header, "")
#         if xerror:
#             # Break on first found.
#             break
#     logger.debug("%s of %s: %s %s", httpVerb, url, resp.status_code, resp.reason)
#     return resp, xcache, xerror


def listMetaTags(self, context):
    # Lists meta tags helper.
    # Creates a mapping of meta tags -> values for the listMetaTags script.
    result = {}
    mt = getToolByName(self, "portal_membership")

    registry = getUtility(IRegistry)
    site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)

    try:
        use_all = site_settings.exposeDCMetaTags
    except AttributeError:
        use_all = False

    security_settings = registry.forInterface(ISecuritySchema, prefix="plone")
    view_about = (
        security_settings.allow_anon_views_about or not mt.isAnonymousUser()
    )

    if not use_all:
        metadata_names = {"Description": METADATA_DCNAME["Description"]}
    else:
        metadata_names = METADATA_DCNAME
    for accessor, key in metadata_names.items():
        # check non-public properties
        if not view_about and accessor in METADATA_DC_AUTHORFIELDS:
            continue

        # short circuit non-special cases
        if not use_all and accessor not in ("Description", "Subject"):
            continue

        method = getattr(aq_inner(context).aq_explicit, accessor, None)
        if not callable(method):
            continue

        # Catch AttributeErrors raised by some AT applications
        try:
            value = method()
        except AttributeError:
            value = None

        if not value:
            # No data
            continue
        if accessor == "Publisher" and value == "No publisher":
            # No publisher is hardcoded (TODO: still?)
            continue

        # Check for fullnames
        if view_about and accessor in METADATA_DC_AUTHORFIELDS:
            if not isinstance(value, (list, tuple)):
                value = [value]
            tmp = []
            for userid in value:
                # Comento la llamada a getMemberInfo para evitar consultas LDAP innecesarias
                # member = mt.getMemberInfo(userid)
                name = userid
                # if member:
                #     name = member["fullname"] or userid
                tmp.append(name)
            value = tmp

        if isinstance(value, (list, tuple)):
            # convert a list to a string
            value = ", ".join(value)

        # Special cases
        if accessor == "Description":
            result["description"] = value
        elif accessor == "Subject":
            result["keywords"] = value

        if use_all:
            result[key] = value

    if use_all:
        created = context.CreationDate()

        try:
            effective = context.EffectiveDate()
            if effective == "None":
                effective = None
            if effective:
                effective = DateTime(effective)
        except AttributeError:
            effective = None

        try:
            expires = context.ExpirationDate()
            if expires == "None":
                expires = None
            if expires:
                expires = DateTime(expires)
        except AttributeError:
            expires = None

        # Filter out DWIMish artifacts on effective / expiration dates
        if (
            effective is not None
            and effective > FLOOR_DATE
            and effective != created
        ):
            eff_str = effective.Date()
        else:
            eff_str = ""

        if expires is not None and expires < CEILING_DATE:
            exp_str = expires.Date()
        else:
            exp_str = ""

        if eff_str or exp_str:
            result["DC.date.valid_range"] = f"{eff_str} - {exp_str}"

    return result
