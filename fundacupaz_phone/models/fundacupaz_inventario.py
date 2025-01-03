# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazInventario(models.Model):
    _inherit = 'product.template'

    ente = fields.Many2one('fundacupaz.ente', string="Ente Origen")


class FundacupazInventarioCampos(models.Model):
    _inherit = 'stock.picking'

    tipo_entrega = fields.Selection(
        selection=[
            ('asi', 'Asignación'),
            ('dot', 'Dotación'),
            ('don', 'Donación'),
        ],
    string='Tipo de Entrega', required=True, tracking=True)