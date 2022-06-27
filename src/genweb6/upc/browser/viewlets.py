# -*- coding: utf-8 -*-
from genweb6.core.browser.viewlets import viewletBase
from genweb6.core.browser.viewlets import footerViewlet as footerViewletBase
from genweb6.core.utils import genwebFooterConfig


class footerViewlet(footerViewletBase):

    def getSignatura(self):
        lang = self.pref_lang()
        footer_config = genwebFooterConfig()
        upc_signatura = "<strong>© UPC</strong>"
        signatura = getattr(footer_config, 'signatura_' + lang)
        return upc_signatura + " " + signatura if signatura else upc_signatura

    def getLinksPeu(self):
        lang = self.pref_lang()

        links = {"ca": {"contact":       {"url": self.root_url() + "/ca/contact", "target": "_self"},
                        "sitemap":       {"url": self.root_url() + "/ca/sitemap", "target": "_self"},
                        "accessibility": {"url": self.root_url() + "/accessibilitat", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/ca/avis-legal", "target": "_blank"},
                        "cookies":       {"url": self.root_url() + "/politica-de-cookies", "target": "_self"}},

                 "es": {"contact":       {"url": self.root_url() + "/es/contact", "target": "_self"},
                        "sitemap":       {"url": self.root_url() + "/es/sitemap", "target": "_self"},
                        "accessibility": {"url": self.root_url() + "/accesibilidad", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/es/aviso-legal", "target": "_blank"},
                        "cookies":       {"url": self.root_url() + "/politica-de-cookies-es", "target": "_self"}},

                 "en": {"contact":       {"url": self.root_url() + "/en/contact", "target": "_self"},
                        "sitemap":       {"url": self.root_url() + "/en/sitemap", "target": "_self"},
                        "accessibility": {"url": self.root_url() + "/accessibility", "target": "_self"},
                        "disclaimer":    {"url": "https://www.upc.edu/en/disclaimer", "target": "_blank"},
                        "cookies":       {"url": self.root_url() + "/cookies-policy", "target": "_self"}}}

        return links[lang]


class footerContactViewlet(viewletBase):
    pass
