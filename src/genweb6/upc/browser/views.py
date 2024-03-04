# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.memoize.view import memoize_contextless
from zope.annotation.interfaces import IAnnotations

from genweb6.core.utils import portal_url
from genweb6.upc import _

import requests

class Cookies(BrowserView):

    @memoize_contextless
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

    @memoize_contextless
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


class RSS(BrowserView):

    @memoize_contextless
    def html(self):
        lang = self.context.language
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'

        templates = {'ca': '/++theme++genweb6.upc/templates/rss-ca.html',
                     'es': '/++theme++genweb6.upc/templates/rss-es.html',
                     'en': '/++theme++genweb6.upc/templates/rss-en.html'}

        page = requests.get(portal_url() + templates[lang])
        if page.status_code == 200:
            return page.content
        else:
            return None


MESSAGE_TEMPLATE = u"""\
L'usuari %(user_name)s ha creat un nou esdeveniment en l'agenda del GenWeb \
"%(titolGW)s":

Títol: "%(titleEvent)s"
Data: %(dayEvent)s-%(monthEvent)s-%(yearEvent)s
Hora: %(hourEvent)s

i que podreu trobar al següent enllaç:

%(linkEvent)s

Per a la seva publicació a l'Agenda general de la UPC.
"""

class sendEventView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        annotations = IAnnotations(context)
        event_title = context.Title()
        event_day = DateTime().day()
        event_month = DateTime().month()
        event_year = DateTime().year()
        event_hour = DateTime().Time()
        event_link = context.absolute_url()
        mailhost = getToolByName(context, 'MailHost')
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        email_charset =  api.portal.get_registry_record('plone.email_charset')
        to_address = 'agenda.web@upc.edu'
        from_name = api.portal.get_registry_record('plone.email_from_name')
        from_address = api.portal.get_registry_record('plone.email_from_address')
        titulo_web = portal.getProperty('title')
        mtool = self.context.portal_membership
        userid = mtool.getAuthenticatedMember().id
        source = "%s <%s>" % (from_name, from_address)
        subject = "[Nou esdeveniment] %s" % (titulo_web)
        message = MESSAGE_TEMPLATE % dict(titolGW=titulo_web,
                                          titleEvent=event_title,
                                          dayEvent=event_day,
                                          monthEvent=event_month,
                                          yearEvent=event_year,
                                          hourEvent=event_hour,
                                          linkEvent=event_link,
                                          from_address=from_address,
                                          from_name=from_name,
                                          user_name=userid)

        mailhost.send(message,
                      to_address,
                      source,
                      subject=subject,
                      msg_type='text/plain',
                      charset=email_charset)

        if 'eventsent' not in annotations:
            annotations['eventsent'] = True

        confirm = _(u"Gràcies per la vostra col·laboració. Les dades de l\'activitat s\'han enviat correctament i seran publicades com més aviat millor.")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())