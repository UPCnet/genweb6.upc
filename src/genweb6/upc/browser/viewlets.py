# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from html import escape
from plone import api
from plone.app.layout.viewlets.common import TitleViewlet
from plone.base.utils import safe_text
from plone.memoize import ram
from plone.memoize.view import memoize_contextless
from zope.component import getMultiAdapter

from genweb6.core.browser.viewlets import footerViewlet as footerViewletBase
from genweb6.core.browser.viewlets import viewletBase
from genweb6.core.utils import genwebFooterConfig
from genweb6.core.utils import genwebHeaderConfig
from genweb6.upc.utils import genwebUPCConfig

import re
from time import time

class footerViewlet(footerViewletBase):

    @ram.cache(lambda *args: time() // (24 * 60 * 60))
    def getSignatura(self):
        lang = self.pref_lang()
        footer_config = genwebFooterConfig()
        upc_signatura = "<strong>© UPC</strong>"
        signatura = getattr(footer_config, 'signatura_' + lang)
        return upc_signatura + " " + signatura if signatura else upc_signatura

    @memoize_contextless
    def getLinksPeu(self):
        lang = self.pref_lang()
        root_url = self.root_url()

        links = {"ca": {"contact":       {},
                        "sitemap":       {"url": root_url + "/ca/sitemap", "target": "_self"},
                        "accessibility": {"url": root_url + "/ca/accessibility", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/ca/avis-legal", "target": "_blank"},
                        "cookies":       {"onClick": "UC_UI.showSecondLayer();", "target": "_self", "url": "#"},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}},

                 "es": {"contact":       {},
                        "sitemap":       {"url": root_url + "/es/sitemap", "target": "_self"},
                        "accessibility": {"url": root_url + "/es/accessibility", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/es/aviso-legal", "target": "_blank"},
                        "cookies":       {"onClick": "UC_UI.showSecondLayer();", "target": "_self", "url": "#"},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}},

                 "en": {"contact":       {},
                        "sitemap":       {"url": root_url + "/en/sitemap", "target": "_self"},
                        "accessibility": {"url": root_url + "/en/accessibility", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/en/disclaimer", "target": "_blank"},
                        "cookies":       {"onClick": "UC_UI.showSecondLayer();", "target": "_self", "url": "#"},
                        "logo":          {"url": "https://genweb.upc.edu/ca", "target": "_blank"}}}

        return links[lang]


class footerContactViewlet(viewletBase):

    @memoize_contextless
    def getContactFormURL(self):
        lang = self.pref_lang()
        root_url = self.root_url()

        if lang == 'es':
            return root_url + '/es/contact'
        elif lang == 'en':
            return root_url + '/en/contact'

        return root_url + '/ca/contact'

    @ram.cache(lambda *args: time() // (24 * 60 * 60))
    def getContactPersonalized(self):
        return genwebUPCConfig().contacte_BBDD_or_page

    @memoize_contextless
    def getContactPage(self):
        """
        Funcio que retorna la pagina de contacte personalitzada
        """
        context = aq_inner(self.context)
        lang = self.context.Language()

        if lang == 'ca':
            customized_page = getattr(context, 'contactepersonalitzat', False)
        elif lang == 'es':
            customized_page = getattr(context, 'contactopersonalizado', False)
        elif lang == 'en':
            customized_page = getattr(context, 'customizedcontact', False)

        try:
            state = api.content.get_state(customized_page)
            if state == 'published':
                return customized_page.text.output
            else:
                return ''
        except:
            return ''


class titleViewlet(TitleViewlet, viewletBase):

    def update(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )

        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )

        page_title = escape(safe_text(context_state.object_title()))
        portal_title = escape(safe_text(portal_state.navigation_root_title()))

        genweb_title = getattr(genwebHeaderConfig(), 'html_title_%s' % self.pref_lang(), 'Genweb UPC')

        if not genweb_title:
            genweb_title = 'Genweb UPC'

        genweb_title = escape(safe_text(re.sub(r'(<.*?>)', r'', genweb_title)))

        marca_UPC = escape(safe_text(u"UPC. Universitat Politècnica de Catalunya"))

        if page_title == portal_title:
            self.site_title = u"%s &mdash; %s" % (genweb_title, marca_UPC)
        else:
            self.site_title = u"%s &mdash; %s &mdash; %s" % (page_title, genweb_title, marca_UPC)
