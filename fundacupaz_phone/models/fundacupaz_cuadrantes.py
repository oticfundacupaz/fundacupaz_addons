# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazCuadrantes(models.Model):
    _name = "fundacupaz.cuadrante"
    _inherit = "mail.thread"

    name = fields.Char("Nombre Cuadrante")
    estado = fields.Many2one(
        'res.country.state',
        domain=[('country_id.name','=','Venezuela')],
        string="Estado", tracking=True
    )
    municipio = fields.Many2one('res.country.state.municipality' ,domain="[('state_id','=', estado)]", string="Municipio", tracking=True)
