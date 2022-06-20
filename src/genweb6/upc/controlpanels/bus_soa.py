# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


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
