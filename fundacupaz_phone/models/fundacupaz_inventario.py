# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazContactos(models.Model):
    _inherit = 'res.partner'

    ente = fields.Many2one('fundacupaz.ente', string="Ente Origen")


class FundacupazInventario(models.Model):
    _inherit = 'product.template'

    ente = fields.Many2one('fundacupaz.ente', string="Ente Origen")


class FundacupazInventarioCampos(models.Model):
    _inherit = 'stock.picking'

    tipo_entrega = fields.Selection(
        selection=[
            ('asi', 'ASIGNACIÓN'),
            ('dot', 'DOTACIÓN'),
            ('don', 'DONACIÓN'),
        ], string='Tipo de Entrega', tracking=True)

    def get_month_name(self, date):
        if date:
            months = [
                "enero", "febrero", "marzo", "abril",
                "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"
            ]
            month_index = date.month - 1
            return months[month_index]
        return ''
