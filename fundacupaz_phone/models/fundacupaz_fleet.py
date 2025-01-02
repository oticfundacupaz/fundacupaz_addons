# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazFleet(models.Model):
    _inherit = 'fleet.vehicle'

    serial_vin = fields.Char('Serial Carroceria')
    beneficiario = fields.Many2one('res.partner', 'Beneficiario', tracking=True, help='Driver address of the vehicle', copy=False)
    ente = fields.Many2one('res.partner', 'Ente', tracking=True, help='Driver address of the vehicle', copy=False)
    acta_asig = fields.Char('Acta de Asignacion')
    estatus = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('GUARDIA CUSTODIA', 'GUARDIA CUSTODIA'),
            ('DISPONIBLE', 'DISPONIBLE'),
            ('INOPERATIVA', 'INOPERATIVA')
        ],
    )
    tipo = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('PATRULLAS', 'PATRULLAS'),
            ('MOTOS', 'MOTOS'),
            ('AMBULANCIA', 'AMBULANCIA'),
            ('MAESTRANZA', 'MAESTRANZA')
        ],

    )
    bl = fields.Char('BL')
    ano = fields.Char('Año Vehiculo')
    color= fields.Char('Color')
    organo = fields.Many2one('res.partner', 'Organo', tracking=True, help='Driver address of the vehicle', copy=False)
    OBSERVACIONES = fields.Char('OBSERVACIONES')
