# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as ZopeViewPageTemplateFile
from zope.component import getMultiAdapter

from genweb6.core.browser.viewlets import viewletBase

import socket


class gwUPCFooter(viewletBase):

    def get_go_to_top_link(self, template, view):

        name = ''
        if isinstance(template, ViewPageTemplateFile) or \
           isinstance(template, ZopeViewPageTemplateFile) or \
           isinstance(template, ViewMixinForTemplates):
            # Browser view
            name = view.__name__
        else:
            if hasattr(template, 'getId'):
                name = template.getId()

        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name=u'plone_context_state')

        if name and name in context_state.current_base_url():
            # We are dealing with a view
            if '@@' in context_state.current_page_url():
                name = '@@{}'.format(name)

            return '{}/{}#portal-header'.format(self.context.absolute_url(), name)
        else:
            # We have a bare content
            return '{}#portal-header'.format(self.context.absolute_url())

    def getLinksPeu(self):
        """ links fixats per accessibilitat/rss/about """
        idioma = self.pref_lang()
        if idioma not in ['ca', 'es', 'en']:
            idioma = 'ca'

        footer_links = {"ca": {"rss": "rss-ca",
                               "accessibility": "accessibilitat",
                               "disclaimer": "https://www.upc.edu/ca/avis-legal",
                               "cookies": self.root_url() + '/politica-de-cookies'
                               },
                        "es": {"rss": "rss-es",
                               "accessibility": "accesibilidad",
                               "disclaimer": "https://www.upc.edu/es/aviso-legal",
                               "cookies": self.root_url() + '/politica-de-cookies-es'
                               },
                        "en": {"rss": "rss-en",
                               "accessibility": "accessibility",
                               "disclaimer": "https://www.upc.edu/en/disclaimer",
                               "cookies": self.root_url() + '/cookies-policy'
                               },
                        }

        return footer_links[idioma]

    def checkIsAdmin(self):
        # Check if user has admin role to show the bottom information box
        # (only for managers)
        if api.user.is_anonymous():
            # is anon
            canViewContent = False
        else:
            # Is a validated user...
            username = api.user.get_current().getProperty('id')
            # get username
            roles = api.user.get_roles(username=username)
            # And check roles
            if 'Manager' in roles:
                canViewContent = True
            else:
                canViewContent = False
        return canViewContent

    def serverInfo(self):
        data = {}
        data['Hostname'] = socket.gethostname()
        data['IP'] = socket.gethostbyname(socket.gethostname())
        data['Port'] = self.request.environ['SERVER_PORT']
        data['Plone'] = api.env.plone_version()
        data['Zope'] = api.env.zope_version()

        in_debug_mode = api.env.debug_mode()
        if in_debug_mode:
            data['Debug'] = "-  Zope is in debug mode"
        else:
            data['Debug'] = ""

        return data

    def getHomeLink(self):
        lang = self.pref_lang()
        if lang == "ca":
            home_link = 'https://www.upc.edu/ca'
        elif lang == "es":
            home_link = 'https://www.upc.edu/es'
        elif lang == "en":
            home_link = 'https://www.upc.edu/en'
        else:
            home_link = 'https://www.upc.edu/ca'

        return home_link
