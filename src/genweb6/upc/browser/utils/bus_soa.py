# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from genweb6.core.utils import json_response
from genweb6.upc.browser.utils.identitat_digital import identitatDigitalUserInfo
from genweb6.upc.utils import genwebBusSOAConfig

import requests


def busSoaInfoUserAltaTFE(self):
    est = identitatDigitalUserInfo(self)
    if 'error' not in est:
        est_colectius = est['uePerfil']

        for col in est_colectius:
            if col['perfilId'] in ['EST', 'ESTMASTER']:
                bussoa_tool = genwebBusSOAConfig()
                result = requests.get(bussoa_tool.bus_url + "/" + col['idOrigen'] + '?tipusAltaTFE=I&numDocument=' + est['document'], headers={'apikey': bussoa_tool.bus_apikey}, auth=(bussoa_tool.bus_user, bussoa_tool.bus_password))

                return result.json()

        return {'error': 'Bus SOA'}

    return est


class BSUserInfoAltaTFE(BrowserView):

    @json_response
    def __call__(self):
        return busSoaInfoUserAltaTFE(self)
