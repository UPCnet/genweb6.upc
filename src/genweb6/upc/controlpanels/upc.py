# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.ramcache import ram

from genweb6.upc import _

import logging

log = logging.getLogger('genweb6.upc')


class IXarxesSocials(model.Schema):

    title = schema.TextLine(
        title=_(u'Títol'),
        required=False
    )

    icon = schema.TextLine(
        title=_(u'Icona'),
        required=False
    )

    url = schema.TextLine(
        title=_(u'Enllaç'),
        required=False
    )


class ITableEmailContact(model.Schema):

    language = schema.Choice(
        title=_(u'Language'),
        vocabulary=u'plone.app.vocabularies.SupportedContentLanguages',
        required=False
    )

    name = schema.TextLine(
        title=_(u'Name'),
        required=False
    )

    email = schema.TextLine(
        title=_(u'E-mail'),
        required=False
    )


class IUPCSettings(model.Schema):

    contacte_al_peu = schema.Bool(
        title=_(u"contacte_al_peu"),
        required=False,
        default=False,
    )

    read_permission(contacte_id='genweb.webmaster')
    write_permission(contacte_id='genweb.manager')
    contacte_id = schema.TextLine(
        title=_(u"contacte_id"),
        required=False,
    )

    custom_map_address = schema.TextLine(
        title=_(u"Adreça del mapa customitzat"),
        description=_(u"Al omplir aquesta dada es modificará la direcció del mapa per la indicada en aquest camp."),
        required=False,
    )

    contacte_BBDD_or_page = schema.Bool(
        title=_(u"contacte_BBBDD_or_page"),
        description=_(u"help_contacte_BBBDD_or_page"),
        required=False,
        default=False,
    )

    treu_enllac_contacte = schema.Bool(
        title=_(u"treu_enllac_contacte"),
        required=False,
        default=False,
    )

    treu_icones_xarxes_socials = schema.Bool(
        title=_(u"treu_icones_xarxes_socials"),
        required=False,
        default=False,
    )

    directives.widget(xarxes_socials=DataGridFieldFactory)
    xarxes_socials = schema.List(
        title=_(u'Xarxes Socials'),
        description=_(u"Icona que es mostrarà, podeu trobar tots els identificadors en el <a href='https://icons.getbootstrap.com/' target='_blank'>següent enllaç</a>. Ex: bi-facebook"),
        value_type=DictRow(schema=IXarxesSocials),
        required=False,
    )

    contacte_multi_email = schema.Bool(
        title=_(u"multi_email"),
        description=_(u"help_contacte_multi_email"),
        required=False,
        default=False,
    )

    directives.widget(contact_emails_table=DataGridFieldFactory)
    contact_emails_table = schema.List(
        title=_(u'Contact emails'),
        description=_(u'help_emails_table'),
        value_type=DictRow(schema=ITableEmailContact),
        required=False,
    )


class UPCSettingsForm(controlpanel.RegistryEditForm):

    schema = IUPCSettings
    label = _(u'Contact')

    def updateFields(self):
        super(UPCSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(UPCSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        replace_contact_emails_table = []
        contact_emails_table = data.get('contact_emails_table', [])
        if contact_emails_table:
            for contact in contact_emails_table:
                contact['language'] = contact['language'][0]
                replace_contact_emails_table.append(contact)

        data['contact_emails_table'] = replace_contact_emails_table
        self.applyChanges(data)
        ram.caches.clear()

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class UPCSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = UPCSettingsForm
