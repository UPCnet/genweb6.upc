# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

# from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
# from collective.z3cform.datagridfield.registry import DictRow
from plone import api
from plone.app.registry.browser import controlpanel
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form import button
from zope import schema
from zope.component import getUtility

from genweb6.core import _

import logging

log = logging.getLogger('genweb6.upc')


class ITableEmailContact(model.Schema):

    language = schema.Choice(
        title=_(u'Language'),
        vocabulary=u'plone.app.vocabularies.SupportedContentLanguages',
        required=False
    )

    name = schema.TextLine(title=_(u'Name'),
                           required=False)
    email = schema.TextLine(title=_(u'E-mail'),
                            required=False)


class IUPCSettings(model.Schema):

    model.fieldset('Contact information', _(u'Contact information'),
                   fields=['contacte_id', 'contacte_BBDD_or_page', 'contacte_al_peu',
                           'directori_upc', 'directori_filtrat', 'contacte_no_upcmaps',
                           'contacte_multi_email'])

    # model.fieldset('Contact information', _(u'Contact information'),
    #                fields=['contacte_id', 'contacte_BBDD_or_page', 'contacte_al_peu',
    #                        'directori_upc', 'directori_filtrat', 'contacte_no_upcmaps',
    #                        'contacte_multi_email', 'contact_emails_table'])

    contacte_id = schema.TextLine(
        title=_(u"contacte_id",
                default=u"ID contacte de la unitat"),
        description=_(u"help_contacte_id",
                      default=u"Afegiu el id de contacte de la base de dades de màsters."),
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

    contacte_al_peu = schema.Bool(
        title=_(u"contacte_al_peu",
                default=u"Adreça de contacte al peu"),
        description=_(u"help_contacte_al_peu",
                      default=u"La informació provinent de la base de dades de SCP es visualitzen al peu de la pàgina."),
        required=False,
        default=False,
    )

    directori_upc = schema.Bool(
        title=_(u"directori_upc",
                default=u"Directori UPC a les eines"),
        description=_(u"help_directori_upc",
                      default=u"Es mostrarà a la part superior l'enllaç al Directori UPC."),
        required=False,
        default=False,
    )

    directori_filtrat = schema.Bool(
        title=_(u"directori_filtrat",
                default=u"Directori UPC filtrat a les eines"),
        description=_(u"help_directori_filtrat",
                      default=u"S'obrirà el Directori UPC, carregant les dades de la unitat."),
        required=False,
        default=False,
    )

    contacte_no_upcmaps = schema.Bool(
        title=_(u"contacte_no_upcmaps",
                default=u"Contacte sense UPCmaps"),
        description=_(u"help_contacte_no_upcmaps",
                      default=u"Es mostra la informació d'UPCmaps al contacte."),
        required=False,
        default=False,
    )

    contacte_multi_email = schema.Bool(
        title=_(u"multi_email",
                default=u"Seleccionar l'adreça d'enviament"),
        description=_(u"help_contacte_multi_email",
                      default=u"Es pot seleccionar a qui s'envia el missatge de contacte."),
        required=False,
        default=False,
    )

    # contact_emails_table = schema.List(
    #     title=_(u'Contact emails'),
    #     description=_(u'help_emails_table',
    #                   default=u'Add name and email by language'),
    #     value_type=DictRow(title=_(u'help_email_table'),
    #                        schema=ITableEmailContact),
    #     required=False,
    # )


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

        try:
            self.applyChanges(data)
        except:
            registry = getUtility(IRegistry)
            # rec = registry.records
            # keys = [a for a in rec.keys()]
            # for k in keys:
            #     try:
            #         rec[k]
            #     except:
            #         if k == 'genweb6.upc.controlpanel.IUPCSettings.contact_emails_table':
            #             old_values = data['contact_emails_table']
            #             registry.records[k] = Record(field.List(title=_(u'Contact emails'), description=_(u'help_emails_table', default=u'Add name and email by language'), value_type=DictRow(title=_(u'help_email_table'), schema=ITableEmailContact), required=False))
            #             api.portal.set_registry_record(name='genweb6.upc.controlpanel.IUPCSettings.contact_emails_table', value=old_values)
            #             log.error('Errors in contropanel? Solved field contact_emails_table in ' + self.context.absolute_url())

            IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
            self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class UPCSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = UPCSettingsForm


class IBusSOASettings(model.Schema):

    bus_url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'URL to access the bus'),
        required=False,
    )

    bus_user = schema.TextLine(
        title=_(u'User'),
        description=_('User to connect to the bus'),
        required=False,
    )

    bus_password = schema.Password(
        title=_(u'Password'),
        required=False,
    )

    bus_apikey = schema.Password(
        title=_(u'APIKEY'),
        required=False,
    )


class BusSOASettingsForm(controlpanel.RegistryEditForm):

    schema = IBusSOASettings
    label = _(u'Bus SOA Settings')

    def updateFields(self):
        super(BusSOASettingsForm, self).updateFields()

    def updateWidgets(self):
        super(BusSOASettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class BusSOASettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = BusSOASettingsForm


class IIdentitatDigitalSettings(model.Schema):

    identitat_url = schema.TextLine(
        title=_(u'URL'),
        description=_(u'URL to access the digital identity'),
        required=False,
    )

    identitat_apikey = schema.Password(
        title=_(u'APIKEY'),
        required=False,
    )


class IdentitatDigitalSettingsForm(controlpanel.RegistryEditForm):

    schema = IIdentitatDigitalSettings
    label = _(u'Identitat Digital Settings')

    def updateFields(self):
        super(IdentitatDigitalSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(IdentitatDigitalSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class IdentitatDigitalSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = IdentitatDigitalSettingsForm