# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable

from zope.interface import implementer

from genweb6.core.cas.controlpanel import setupCAS


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


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('genweb6.upc_various.txt') is None:
        return

    setupCAS("https://sso.upc.edu/CAS/", "genweb", "UPC")
