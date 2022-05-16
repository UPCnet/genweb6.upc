# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.content import Container
from pyquery import PyQuery as pq
from requests.exceptions import ReadTimeout
from requests.exceptions import RequestException
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter, getAdapters
from zope.interface import implementer
from zope.interface import Interface

from genweb6.core import utils
from genweb6.upc import _
from genweb6.upc.content.packet import PACKETS_KEY

import plone.api
import re
import requests
import urllib.parse


class Ipacket(IFolder):
    """Marker interface for the packet"""


@implementer(Ipacket)
class Packet(Container):
    pass


class IpacketDefinition(Interface):
    """A packet definition"""

    order = schema.Int(title=u"Order")
    URL_schema = schema.TextLine(title=u"The URL schema of the packet")


class View(BrowserView):

    template = ViewPageTemplateFile('templates/view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.title = ''
        self.content = ''

    def __call__(self):
        return self.template()

    def get_catalog_content(self, path_to_search):
        """ Fem una consulta al catalog, en comptes de fer un PyQuery """
        raw_html = u''
        catalog = getToolByName(self.context, 'portal_catalog')

        objects = catalog(path=path_to_search)
        try:
            raw_html = objects[0]()
        except:
            raw_html = objects[0].getObject()()

        return raw_html

    def getHTML(self):
        packet_type = self.getType()
        adapter = getAdapter(self.context, IpacketDefinition, packet_type)
        adapter.packet_fields.update({'lang': utils.pref_lang()})

        url = adapter.URL_schema
        portal_url = getToolByName(self.context, "portal_url")
        portal = portal_url.getPortalObject()
        url_portal_nginx = portal.absolute_url()  # url (per dns) del lloc

        try:
            url = self.get_absolute_url(url % adapter.packet_fields)
            # check url to avoid autoreference, removing http(s) and final slash
            link_url = re.findall('https?://(.*)', url)[0].strip('/')  # url del contingut netejada
            parent_url = re.findall('https?://(.*)', self.context.absolute_url())[0].strip('/')  # url del pare netejada
            root_url = re.findall('https?://(.*)', url_portal_nginx)[0].strip('/')  # url (per dns) del lloc netejada
            if link_url != parent_url:
                if link_url.startswith(root_url):
                    # link intern, search through the catalog
                    relative_path = '/' + re.findall(root_url + '(.*)', link_url)[0]
                    url_to_search = '/'.join(portal.getPhysicalPath()) + relative_path
                    raw_html = self.get_catalog_content(url_to_search)
                    clean_html = re.sub(r'[\n\r]?', r'', raw_html)
                    doc = pq(clean_html)
                    match = re.search(r'This page does not exist', clean_html)
                    self.title = self.context.Title()  # titol per defecte
                    if not match:
                        if packet_type == 'contingut_genweb':
                            element = adapter.packet_fields['element']
                            if not element:
                                element = "#content-core"
                        else:
                            element = "#content-nucli"
                        content = pq('<div/>').append(
                            doc(element).outerHtml()).html(method='html')
                        if not content:
                            content = _(u"ERROR. This element does not exist.") + " " + element
                    else:
                        content = _(u"ERROR: Unknown identifier. This page does not exist." + url)
                else:
                    # link extern, pyreq
                    raw_html = requests.get(url, timeout=5, verify=False)
                    clean_html = re.sub(r'[\n\r]?', r'', raw_html.text)
                    doc = pq(clean_html)
                    match = re.search(r'This page does not exist', clean_html)
                    self.title = self.context.Title()  # titol per defecte
                    if not match:
                        if packet_type == 'contingut_genweb':
                            element = adapter.packet_fields['element']
                            if not element:
                                element = "#content-core"
                        else:
                            element = "#content-nucli"
                        content = pq('<div/>').append(
                            doc(element).outerHtml()).html(method='html')
                        if not content:
                            content = _(u"ERROR. This element does not exist.") + " " + element
                    else:
                        content = _(u"ERROR: Unknown identifier. This page does not exist." + url)
            else:
                content = _(u"ERROR. Autoreference")
        except ReadTimeout:
            content = _(u"ERROR. There was a timeout while waiting for '{0}'".format(self.get_absolute_url(self.data.url)))
        except RequestException:
            content = _(u"ERROR. This URL does not exist.")
        except:
            content = _(u"ERROR. Unexpected exception.")

        self.content = content

    def get_absolute_url(self, url):
        """
        Convert relative url to absolute
        """
        if not ("://" in url):
            base = self.context.__parent__.absolute_url() + '/'
            return urllib.parse.urljoin(base, url)
        else:
            # Already absolute
            return url

    def getPacket(self):
        return self.content

    def getTitle(self):
        # import pdb; pdb.set_trace()
        # si el contingut esta configurat i encara no tenim el content, l'obtenim
        # el titol sera el nom del contingut (llistat, paquet o genweb) o el nom de l'estudi
        if self.isAlreadyConfigured() and self.content == '':
            self.getHTML()
        return self.title

    def getType(self):
        annotations = IAnnotations(self.context)
        return annotations.get(PACKETS_KEY + '.type', None)

    def isAlreadyConfigured(self):
        annotations = IAnnotations(self.context)
        if annotations.get(PACKETS_KEY + '.type', None):
            return True
        else:
            return False

    def selectedPacket(self):
        annotations = IAnnotations(self.context)
        packet_key = annotations.get(PACKETS_KEY + '.type')
        packet_fields = annotations.get(PACKETS_KEY + '.fields')
        packet_mapui = annotations.get(PACKETS_KEY + '.mapui')

        return dict(packet_key=packet_key, value=packet_fields.get(packet_mapui.get('codi')), element=packet_fields.get(packet_mapui.get('element')))

    def show_extended_info(self):
        user = plone.api.user.get_current()

        if getattr(user, 'name', False):
            if user.name == 'Anonymous User':
                return False
        try:
            user_roles = set(plone.api.user.get_roles(user=user, obj=self.context) +
                             plone.api.user.get_roles(user=user))
        except:
            user_roles = set(plone.api.user.get_roles(user=user, obj=self.context))

        if 'Manager' in user_roles or \
           'WebMaster' in user_roles or \
           'Site Administrator' in user_roles or \
           'Owner' in user_roles:
            return True
        else:
            return False

    def absolute_url(self, url):
        """
        Convert relative url to absolute
        """
        if not ("://" in url):
            base = self.context.__parent__.absolute_url() + '/'
            return urllib.parse.urljoin(base, url)
        else:
            # Already absolute
            return url


class Configure(BrowserView):

    template = ViewPageTemplateFile('templates/configure.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.available_ptypes = sorted([adapter for adapter in getAdapters((self.context,), IpacketDefinition)], key=lambda adapter: adapter[1].order)

    def __call__(self):
        if self.request.form:
            form = self.request.form
            packet_type = form.get("packet_type", None)
            if packet_type:
                adapter = getAdapter(self.context, IpacketDefinition, packet_type)
                field_values = dict([(field, form[field]) for field in adapter.fields])
                adapter.packet_fields = field_values
                adapter.packet_type = packet_type
                adapter.packet_mapui = adapter.mapui
                return self.request.response.redirect(self.context.absolute_url())
        return self.template()

    def getAvailablePacketsInfo(self):
        return self.available_ptypes

    def getTitle(self):
        return self.context.Title()

    def selectedPacket(self):
        if self.isAlreadyConfigured():
            annotations = IAnnotations(self.context)
            packet_key = annotations.get(PACKETS_KEY + '.type')
            packet_fields = annotations.get(PACKETS_KEY + '.fields')
            packet_mapui = annotations.get(PACKETS_KEY + '.mapui')
            selected = dict(packet_key=packet_key, value=packet_fields.get(packet_mapui.get('codi')), element=packet_fields.get(packet_mapui.get('element')))
        else:
            selected = {'packet_key': '', 'value': '', 'element': ''}

        return selected

    def isAlreadyConfigured(self):
        annotations = IAnnotations(self.context)
        if annotations.get(PACKETS_KEY + '.type', None):
            return True
        else:
            return False

    def getType(self):
        annotations = IAnnotations(self.context)
        return annotations.get(PACKETS_KEY + '.type', None)
