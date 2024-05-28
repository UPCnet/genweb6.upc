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
from genweb6.upc.browser.utils.event_creator import EventCreator

import requests
import json

from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zExceptions import BadRequest
import base64
import logging
from genweb6.core.utils import genwebHeaderConfig


class Cookies(BrowserView):

    @memoize_contextless
    def html(self):
        lang = self.context.language
        if lang not in ['ca', 'es', 'en']:
            lang = 'ca'

        templates = {
            'ca': '/++theme++genweb6.upc/templates/politica-de-cookies.html',
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
"%(gw_title)s":

Títol: "%(gw_event_title)s"

i que podreu trobar al següent enllaç:

%(created_event_link)s

Per a la seva publicació a l'Agenda general de la UPC.
"""


class sendEventView(BrowserView):

    RECIPIENT_ADDRESS = 'plone.team@upcnet.es'

    def __call__(self):
        """ This view creates an event on the UPC Agenda and then informs
        the administrator of the website about the new event."""
        alsoProvides(self.request, IDisableCSRFProtection)
        event_data = self.get_event_data()
        mailhost, url_tool, membership_tool = self.get_tools()
        portal = url_tool.getPortalObject()
        genweb_title = getattr(genwebHeaderConfig(), 'html_title_%s' % portal.language, 'Genweb UPC')

        created_event_data = None
        event_creator = EventCreator(event_data)

        # Handle event creation on remote website
        try:
            created_event_data = self.handle_event_creation(event_creator)
        except BadRequest as e:
            IStatusMessage(self.request).addStatusMessage(str(e), type='error')
            return self.request.response.redirect(self.context.absolute_url())
        except Exception as e:
            IStatusMessage(self.request).addStatusMessage(
                "No s'ha pogut enviar l'esdeveniment", type='error')
            logging.error(f"Error creating event: {str(e)}")
            return self.request.response.redirect(self.context.absolute_url())

        if created_event_data is None:
            IStatusMessage(self.request).addStatusMessage(
                "No s'ha pogut enviar l'esdeveniment", type='error')
            return self.request.response.redirect(self.context.absolute_url())

        email_charset, from_name, from_address = self.get_registry_records()

        message = self.build_email_message(
            membership_tool, event_data['title'], created_event_data['@id'], genweb_title)

        self.send_email(mailhost, message, from_name,
                        from_address, genweb_title, email_charset)
        self.handle_annotations()
        self.handle_success()

    def get_event_data(self):
        start = self.parse_dates('start')
        end = self.parse_dates('end')

        image_data = self.get_image_data(self.context.image)
        text_data = self.get_text_data(self.context.text)

        return {
            'title': self.context.Title(),
            'start': start,
            'end': end,
            'description': self.context.Description(),
            'location': getattr(self.context, 'location', ''),
            'whole_day': getattr(self.context, 'whole_day', False),
            'open_end': getattr(self.context, 'open_end', False),
            'contact_name': getattr(self.context, 'contact_name', ''),
            'contact_email': getattr(self.context, 'contact_email', ''),
            'contact_phone': getattr(self.context, 'contact_phone', ''),
            'event_url': getattr(self.context, 'event_url', ''),
            'text': text_data,
            'created_event_url': self.context.absolute_url(),
            '@type': self.context.portal_type,
            'imatge': image_data,
        }

    def parse_dates(self, field_name):
        """ Get string representation of date fields """
        date = getattr(self.context, field_name, '')
        if date:
            date = date.isoformat()

        return date

    def get_image_data(self, image):
        if image is None:
            return {}
        binary_data = image.data
        b64_data = base64.b64encode(binary_data)
        b64_string = b64_data.decode('utf-8')

        return {
            'data': b64_string,
            'size': image.getSize(),
            'encoding': 'base64',
            'filename': image.filename,
            'content-type': image.contentType
        }

    def get_text_data(self, text):
        if text is None:
            return ''

        return text.output

    def get_tools(self):
        """ Get Plone tools"""
        mailhost = getToolByName(self.context, 'MailHost')
        url_tool = getToolByName(self.context, 'portal_url')
        membership_tool = self.context.portal_membership
        return mailhost, url_tool, membership_tool

    def handle_event_creation(self, ec):
        ec.authenticate()
        if not ec.is_authenticated:
            raise BadRequest("L'autenticació ha fallat. No es pot fer la petició.")

        return ec.create_event()

    def get_registry_records(self):
        email_charset = api.portal.get_registry_record('plone.email_charset')
        from_name = api.portal.get_registry_record('plone.email_from_name')
        from_address = api.portal.get_registry_record('plone.email_from_address')

        return email_charset, from_name, from_address

    def build_email_message(
            self, membership_tool, gw_event_title, created_event_link, web_title):
        userid = membership_tool.getAuthenticatedMember().id

        message = MESSAGE_TEMPLATE % dict(gw_title=web_title,
                                          gw_event_title=gw_event_title,
                                          created_event_link=created_event_link,
                                          user_name=userid)
        return message

    def send_email(
            self, mailhost, message, from_name, from_address, web_title, email_charset):
        source = "%s <%s>" % (from_name, from_address)
        subject = "[Nou esdeveniment] %s" % (web_title)
        mailhost.send(message,
                      self.RECIPIENT_ADDRESS,
                      source,
                      subject=subject,
                      msg_type='text/plain',
                      charset=email_charset)

    def handle_annotations(self):
        """ Set flag to avoid sending the same event multiple times """
        annotations = IAnnotations(self.context)
        if 'eventsent' not in annotations:
            annotations['eventsent'] = True

    def handle_success(self):
        confirm = _(
            u"Gràcies per la vostra col·laboració. Les dades de l\'esdeveniment s\'han enviat correctament i seran publicades com més aviat millor.")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())
