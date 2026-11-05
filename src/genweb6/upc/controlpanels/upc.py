# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.dexterity.interfaces import IDexteritySchema
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form import button
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.component import getUtility
from zope.interface import Invalid
from zope.ramcache import ram

from genweb6.upc import _
from genweb6.core.purge import purge_varnish_paths

import logging

log = logging.getLogger('genweb6.upc')


class IXarxesSocials(model.Schema, IDexteritySchema):

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


class ITableEmailContact(model.Schema, IDexteritySchema):

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


class IUPCSettings(model.Schema, IDexteritySchema):

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

    contacte_BBDD_or_page = schema.Bool(
        title=_(u"contacte_BBBDD_or_page"),
        description=_(u"help_contacte_BBBDD_or_page"),
        required=False,
        default=False,
    )

    custom_map_address = schema.TextLine(
        title=_(u"Adreça del mapa customitzat"),
        description=_(u"Al omplir aquesta dada es modificará la direcció del mapa per la indicada en aquest camp."),
        required=False,
    )

    read_permission(google_maps_api_key='genweb.manager')
    write_permission(google_maps_api_key='genweb.manager')
    google_maps_api_key = schema.TextLine(
        title=_(u"API Key de Google Maps"),
        description=_(u"API Key de Google Cloud amb la Maps Embed API habilitada. Si es deixa buit, el mapa es mostra amb el format antic."),
        required=False,
    )

    model.fieldset(
        'xarxes_socials',
        label=_(u'Xarxes Socials'),
        fields=['treu_icones_xarxes_socials', 'xarxes_socials'],
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

    model.fieldset(
        'contact_emails',
        label=_(u'Formulari de contacte'),
        fields=['treu_enllac_contacte', 'contacte_multi_email', 'contact_emails_table']
    )

    treu_enllac_contacte = schema.Bool(
        title=_(u"treu_enllac_contacte"),
        description=_(u"help_treu_enllac_contacte"),
        required=False,
        default=False,
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


def registerMissingUPCRecords():
    """ Registra els camps nous que encara no són al registre (webs sense upgrade) """
    registry = getUtility(IRegistry)
    prefix = IUPCSettings.__identifier__ + '.'
    names = schema.getFieldNames(IUPCSettings)
    missing = [name for name in names if prefix + name not in registry.records]
    if missing:
        registry.registerInterface(
            IUPCSettings, omit=[name for name in names if name not in missing])


class UPCSettingsForm(controlpanel.RegistryEditForm):

    schema = IUPCSettings
    label = _(u'Contact')

    def getContent(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(self.schema, check=False)

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

        # Només hi és si l'usuari té permís per editar el camp (genweb.manager)
        if 'google_maps_api_key' in data:
            from genweb6.upc.utils import validateGoogleMapsAPIKey

            api_key = (data['google_maps_api_key'] or '').strip() or None
            data['google_maps_api_key'] = api_key
            if api_key and api_key != self.getContent().google_maps_api_key:
                valid = validateGoogleMapsAPIKey(api_key, self.context.absolute_url() + '/')
                if valid is False:
                    raise WidgetActionExecutionError(
                        'google_maps_api_key',
                        Invalid(_(u"L'API Key no és vàlida o no està autoritzada per a aquest domini.")))
                if valid is None:
                    IStatusMessage(self.request).addStatusMessage(
                        _(u"No s'ha pogut comprovar l'API Key de Google Maps. S'ha desat igualment."), "warning")

        replace_contact_emails_table = []
        contact_emails_table = data.get('contact_emails_table', [])
        if contact_emails_table:
            for contact in contact_emails_table:
                contact['language'] = contact['language'][0]
                replace_contact_emails_table.append(contact)

        data['contact_emails_table'] = replace_contact_emails_table
        registerMissingUPCRecords()
        self.applyChanges(data)
        ram.caches.clear()

        paths = []
        paths.append('/_purge_all')

        purge_varnish_paths(self, paths)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class UPCSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = UPCSettingsForm
