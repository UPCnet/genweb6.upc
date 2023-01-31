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

from genweb6.core import _

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

    model.fieldset('Contact information', _(u'Contact information'),
                   fields=['contacte_al_peu', 'contacte_id',
                           'custom_map_address',
                           'contacte_BBDD_or_page',
                           'treu_icones_xarxes_socials', 'xarxes_socials',
                           'contacte_multi_email', 'contact_emails_table'])

    contacte_al_peu = schema.Bool(
        title=_(u"contacte_al_peu",
                default=u"Adreça de contacte al peu"),
        description=_(u"help_contacte_al_peu",
                      default=u"La informació provinent de la base de dades de SCP es visualitzen al peu de la pàgina."),
        required=False,
        default=False,
    )

    read_permission(contacte_id='genweb.webmaster')
    write_permission(contacte_id='genweb.manager')
    contacte_id = schema.TextLine(
        title=_(u"contacte_id",
                default=u"ID contacte de la unitat"),
        description=_(u"help_contacte_id",
                      default=u"Afegiu el id de contacte de la base de dades de màsters."),
        required=False,
    )

    custom_map_address = schema.TextLine(
        title=_(u"Adreça del mapa customitzat"),
        description=_(u"Al omplir aquesta dada es modificará la direcció del mapa per la indicada en aquest camp."),
        required=False,
    )

    contacte_BBDD_or_page = schema.Bool(
        title=_(u"contacte_BBBDD_or_page",
                default=u"Página de contacte personalitzada"),
        description=_(u"help_contacte_BBBDD_or_page",
                      default=u"Per defecte, la informació de contacte prové de la base de dades de SCP, sota petició."),
        required=False,
        default=False,
    )

    treu_icones_xarxes_socials = schema.Bool(
        title=_(u"treu_icones_xarxes_socials",
                default="Treu les icones per compartir en xarxes socials del peu"),
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
        title=_(u"multi_email",
                default=u"Seleccionar l'adreça d'enviament"),
        description=_(u"help_contacte_multi_email",
                      default=u"Es pot seleccionar a qui s'envia el missatge de contacte."),
        required=False,
        default=False,
    )

    directives.widget(contact_emails_table=DataGridFieldFactory)
    contact_emails_table = schema.List(
        title=_(u'Contact emails'),
        description=_(u'help_emails_table', default=u'Add name and email by language'),
        value_type=DictRow(schema=ITableEmailContact),
        required=False,
    )


class UPCSettingsForm(controlpanel.RegistryEditForm):

    schema = IUPCSettings
    label = _(u'UPC Settings')

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
        for contact in contact_emails_table:
            contact['language'] = contact['language'][0]
            replace_contact_emails_table.append(contact)

        data['contact_emails_table'] = replace_contact_emails_table
        self.applyChanges(data)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class UPCSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = UPCSettingsForm
