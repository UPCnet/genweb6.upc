# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from genweb6.core.utils import portal_url

import requests


class Cookies(BrowserView):

    def html(self):
        lang = self.context.language
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'

        templates = {'ca': '/++theme++genweb6.upc/templates/politica-de-cookies.html',
                     'es': '/++theme++genweb6.upc/templates/politica-de-cookies-es.html',
                     'en': '/++theme++genweb6.upc/templates/cookies-policy.html'}

        page = requests.get(portal_url() + templates[lang])
        if page.status_code == 200:
            return page.content
        else:
            return None


class Accessibility(BrowserView):

    def html(self):
        lang = self.context.language
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'

        templates = {'ca': '/++theme++genweb6.upc/templates/accessibilitat.html',
                     'es': '/++theme++genweb6.upc/templates/accesibilidad.html',
                     'en': '/++theme++genweb6.upc/templates/accessibility.html'}

        page = requests.get(portal_url() + templates[lang])
        if page.status_code == 200:
            return page.content
        else:
            return None
