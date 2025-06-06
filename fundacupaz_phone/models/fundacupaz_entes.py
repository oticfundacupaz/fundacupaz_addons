# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazEntes(models.Model):
    _name = "fundacupaz.ente"
    _rename = "nombre_ente"
    _inherit = "mail.thread"

    name = fields.Char("Nombre Ente")

