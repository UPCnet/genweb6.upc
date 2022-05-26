# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from html import escape
from plone import api
from plone.formwidget.recaptcha.widget import ReCaptchaFieldWidget
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form import button
from z3c.form import field
from z3c.form import widget
from z3c.form.error import ValueErrorViewSnippet
from z3c.form.form import Form
from zope import schema
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema.interfaces import InvalidValue
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core import _ as _core
from genweb6.core.utils import pref_lang
from genweb6.upc.controlpanel import IUPCSettings
from genweb6.upc.utils import genwebUPCConfig

import re


MESSAGE_TEMPLATE_CA = u"""\
Reply-To: %(from_address)s

Heu rebut aquest correu perquè en/na %(name)s (%(from_address)s) ha enviat \
comentaris desde de l'espai Genweb \

%(genweb)s

El missatge és:

%(message)s
--
%(from_name)s
"""

MESSAGE_TEMPLATE_ES = u"""\
Reply-To: %(from_address)s

Ha recibido este correo porque %(name)s (%(from_address)s) ha enviado \
comentarios desde el espacio Genweb \

%(genweb)s

El mensaje es:

%(message)s
--
%(from_name)s
"""

MESSAGE_TEMPLATE_EN = u"""\
Reply-To: %(from_address)s

You received this email because %(name)s (%(from_address)s) it sent \
comments from the Genweb space \

%(genweb)s

The message is:

%(message)s
--
%(from_name)s
"""


@implementer(IVocabularyFactory)
class getEmailsContactNames(object):

    def __call__(self, context):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IUPCSettings, check=False)
        lang = pref_lang()
        items = []

        # if settings.contact_emails_table is not None:
        #     for item in settings.contact_emails_table:
        #         if lang == item['language']:
        #             token = unicodedata.normalize('NFKD', item['name']).encode('ascii', 'ignore').lower()
        #             items.append(SimpleVocabulary.createTerm(
        #                 item['name'],
        #                 token,
        #                 item['name'],))
        return SimpleVocabulary(items)


class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")


check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match


def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True


def is_checked(value):
    if not value:
        raise Invalid(u"")
        return False
    else:
        return True


class IContactForm(model.Schema):
    """Define the fields of our form
    """

    recipient = schema.Choice(
        title=_('to_address', default=u"Recipient"),
        vocabulary="availableContacts",
        required=False
    )

    nombre = schema.TextLine(
        title=_('genweb_sender_fullname', default=u"Name"),
        required=True
    )

    from_address = schema.TextLine(
        title=_('genweb_sender_from_address', default=u"E-Mail"),
        required=True,
        constraint=validate_email
    )

    asunto = schema.TextLine(
        title=_('genweb_subject', default="Subject"),
        required=True
    )

    mensaje = schema.Text(
        title=_('genweb_message', default="Message"),
        description=_("genweb_help_message", default="Please enter the message you want to send."),
        required=True
    )

    privacidad = schema.Bool(
        title=_core('title_privacy'),
        description=_core(u'desc_privacy'),
        required=True,
        constraint=is_checked
    )

    captcha = schema.TextLine(
        title=_(''),
        description=_(''),
        required=True
    )


noValueMessage = widget.StaticWidgetAttribute(
    _core(u'custom message'),
    field=IContactForm['recipient']
)


class ContactForm(Form):

    fields = field.Fields(IContactForm)
    template = ViewPageTemplateFile("contact.pt")
    ignoreContext = True

    # This trick hides the editable border and tabs in Plone
    def update(self):
        self.request.set('disable_border', True)
        self.fields['captcha'].widgetFactory = ReCaptchaFieldWidget
        super(ContactForm, self).update()

    def updateWidgets(self):
        super(ContactForm, self).updateWidgets()
        # Quickfix: Copy the value of the captcha input field to the captcha
        # field of the form. Otherwise the parameter 'form.widgets.captcha'
        # will not be present in the request.
        self.request['form.widgets.captcha'] = self.request.get('recaptcha_response_field')
        # Override the interface forced 'hidden' to 'input' for add form only
        if not api.portal.get_registry_record(name='genweb6.upc.controlpanel.IUPCSettings.contacte_multi_email') or not self.getDataContact():
            self.widgets['recipient'].mode = 'hidden'

    def get_captcha_error_instace(self):
        error_instance = ValueErrorViewSnippet(
            InvalidValue(),
            self.request,
            self.widgets['captcha'],
            self.fields['captcha'].field,
            self.form_instance,
            self.context)
        error_instance.defaultMessage = _core(u"The entered text does not match the text in the image")
        error_instance.update()
        return error_instance

    def captcha_is_invalid(self):
        if self.context.restrictedTraverse('@@recaptcha').verify():
            return False
        if not self.widgets['captcha'].error:
            self.widgets['captcha'].error = self.get_captcha_error_instace()
        return True

    @button.buttonAndHandler(_(u"Send"))
    def action_send(self, action):
        """Send the email to the configured mail address in properties and redirect to the
        front page, showing a status message to say the message was sent.
        """
        data, errors = self.extractData()

        if self.captcha_is_invalid():
            return

        if 'asunto' not in data or \
           'from_address' not in data or \
           'mensaje' not in data or \
           'nombre' not in data or \
           'privacidad' not in data:
            return

        context = aq_inner(self.context)
        mailhost = getToolByName(context, 'MailHost')
        portal = api.portal.get()
        email_charset = api.portal.get_registry_record('plone.email_charset')

        to_address = api.portal.get_registry_record('plone.email_from_address')
        if not to_address:
            to_address = 'scp.admin@upc.edu'

        to_name = api.portal.get_registry_record('plone.email_from_name').encode('utf-8')

        if api.portal.get_registry_record(name='genweb6.upc.controlpanel.IUPCSettings.contacte_multi_email'):
            contact_data = self.getDataContact()
            if contact_data != []:
                if data['recipient']:
                    to_name = data['recipient'].encode("utf-8")
                    for item in contact_data:
                        if to_name in item['name'].encode("utf-8"):
                            if item['email']:
                                to_address = item['email']
                                to_name = to_name
                                continue
                            else:
                                to_address = to_address
                                to_name = 'Genweb amb error al contacte'
                                continue
                else:
                    to_address = to_address
                    to_name = 'Genweb amb error al contacte'
            else:
                to_address = to_address
                to_name = 'Genweb amb error al contacte'

        lang = pref_lang()
        subject = "[Formulari Contacte] %s" % (escape(safe_unicode(data['asunto'])))
        template = MESSAGE_TEMPLATE_CA

        if lang == 'es':
            subject = "[Formulario de Contacto] %s" % (escape(safe_unicode(data['asunto'])))
            template = MESSAGE_TEMPLATE_ES
        if lang == 'en':
            subject = "[Contact Form] %s" % (escape(safe_unicode(data['asunto'])))
            template = MESSAGE_TEMPLATE_EN

        template

        message = template % dict(name=data['nombre'],
                                  from_address=data['from_address'],
                                  genweb=portal.absolute_url(),
                                  message=data['mensaje'],
                                  from_name=data['nombre'])

        mailhost.send(escape(safe_unicode(message)),
                      mto=to_address,
                      mfrom=api.portal.get_registry_record('plone.email_from_address'),
                      subject=subject,
                      charset=email_charset,
                      msg_type='text/plain')

        confirm = _(u"Mail sent.")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')

        self.request.response.redirect('contact_feedback')

        return ''

    def getURLDirectori(self, codi):
        return "https://directori.upc.edu/directori/dadesUE.jsp?id=%s" % codi

    def getURLMaps(self, codi):
        lang = pref_lang()
        return "https://maps.upc.edu/embed/?lang=%s&iu=%s" % (lang, codi)

    def getURLUPCmaps(self, codi):
        lang = self.context.Language()
        return "https://maps.upc.edu/?iu=%s&lang=%s" % (codi, lang)

    def getContactPersonalized(self):
        return genwebUPCConfig().contacte_BBDD_or_page

    def getContactPage(self):
        """
        Funcio que retorna la pagina de contacte personalitzada
        """
        context = aq_inner(self.context)
        lang = self.context.Language()
        if lang == 'ca':
            customized_page = getattr(context, 'contactepersonalitzat', False)
        elif lang == 'es':
            customized_page = getattr(context, 'contactopersonalizado', False)
        elif lang == 'en':
            customized_page = getattr(context, 'customizedcontact', False)

        try:
            state = api.content.get_state(customized_page)
            if state == 'published':
                return customized_page.text.raw
            else:
                return ''
        except:
            return ''

    def getDataContact(self):
        lang = pref_lang()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IUPCSettings, check=False)
        items = []

        # if settings.contact_emails_table is not None:
        #     for item in settings.contact_emails_table:
        #         if lang == item['language']:
        #             items.append(item)
        return items

    def isContactAddress(self):
        if self.getDataContact() or api.portal.get_registry_record('plone.email_from_address'):
            return True
        else:
            return False
