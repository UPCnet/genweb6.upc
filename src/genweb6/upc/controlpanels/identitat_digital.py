# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.registry.browser import controlpanel
from plone.supermodel import model
from z3c.form import button
from zope import schema

from genweb6.core import _


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
