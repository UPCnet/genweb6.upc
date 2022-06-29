# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from genweb6.core.utils import json_response
from genweb6.upc.utils import getTokenIdentitatDigital
from genweb6.upc.utils import genwebIdentitatDigitalConfig

import requests


def identitatDigitalUserInfo(self):
    if self.request.form:
        if 'user' in self.request.form:
            result = getTokenIdentitatDigital()
            if result.status_code == 201:
                identitat_digital_tool = genwebIdentitatDigitalConfig()
                urlGetPerson = identitat_digital_tool.identitat_url + '/gcontrol/rest/externs/persones/' + self.request.form['user'] + '/cn'
                data = requests.get(urlGetPerson, headers={'TOKEN': result.json()['tokenAcl']})
                if data.status_code == 200:
                    return data.json()
                else:
                    return {'error': data.status_code}

    return {'error': 'Not parameter user'}


class IDUserInfo(BrowserView):

    @json_response
    def __call__(self):
        return identitatDigitalUserInfo(self)
