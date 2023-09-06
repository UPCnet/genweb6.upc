# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.admin import AddPloneSite
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.GenericSetup import BASE
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

from plone.base.interfaces import INonInstallable
from plone.base.interfaces import IPloneSiteRoot
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import check as checkCSRF
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.ramcache import ram

import logging

LOGGER = logging.getLogger('Products.CMFPlone')


class addGenwebUPC(AddPloneSite):

    def profiles(self):
        base_profiles = []
        extension_profiles = []
        selected_extension_profiles = (
            'genweb6.upc:default',
        )

        # profiles available for install/uninstall, but hidden at the time
        # the Plone site is created
        not_installable = [
            'Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow',
        ]
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(util.getNonInstallableProfiles())

        for info in profile_registry.listProfileInfo():
            if info.get('type') == EXTENSION and \
               info.get('for') in (IPloneSiteRoot, None):
                profile_id = info.get('id')
                if profile_id not in not_installable:
                    if profile_id in selected_extension_profiles:
                        info['selected'] = 'selected'
                    extension_profiles.append(info)

        def _key(v):
            # Make sure implicitly selected items come first
            selected = v.get('selected') and 'automatic' or 'manual'
            return '{}-{}'.format(selected, v.get('title', ''))
        extension_profiles.sort(key=_key)

        for info in profile_registry.listProfileInfo():
            if info.get('type') == BASE and \
               info.get('for') in (IPloneSiteRoot, None):
                base_profiles.append(info)

        return dict(
            base=tuple(base_profiles),
            default=_DEFAULT_PROFILE,
            extensions=tuple(extension_profiles),
        )

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            site_id = form.get('site_id', 'Plone')

            # CSRF protect. DO NOT use auto CSRF protection for adding a site
            alsoProvides(self.request, IDisableCSRFProtection)

            # check if keyring is installed on root, disable CSRF protection
            # if it is because it is not installed until a plone site
            # is created
            if queryUtility(IKeyManager) is None:
                LOGGER.info('CSRF protection disabled on initial site '
                            'creation')
            else:
                # we have a keymanager, check csrf protection manually now
                checkCSRF(self.request)

            ram.caches.clear()

            site = addPloneSite(
                context, site_id,
                title=form.get('title', ''),
                profile_id=form.get('profile_id', _DEFAULT_PROFILE),
                extension_ids=form.get('extension_ids', ('genweb6.upc:default',)),
                setup_content=form.get('setup_content', False),
                default_language=form.get('default_language', 'en'),
                portal_timezone=form.get('portal_timezone', 'UTC')
            )

            self.request.response.redirect(site.absolute_url() + '/@@setup-view')

            return ''

        return self.index()
