# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazCuadrantes(models.Model):
    _name = "fundacupaz.cuadrante"
    _description = 'Cuadrante de Paz'
    _inherit = "mail.thread"

    name = fields.Char("Nombre Cuadrante", required=True)
    estado = fields.Many2one(
        'res.country.state',
        domain=[('country_id.name','=','Venezuela')],
        string="Estado", tracking=True, required=True

    )
    municipio = fields.Many2one('res.country.state.municipality' ,domain="[('state_id','=', estado)]", string="Municipio", tracking=True, required=True)
    
    circuito_comunal = fields.Char(string='Circuito Comunal', required=True)
    jefe_cuadrante = fields.Many2one('res.partner', string='Jefe de Cuadrantes', required=True)
    Telefono = fields.Char(string="Telefono", tracking=True, required=True)

    Moto = fields.Selection([
        ('si', 'Si'),
        ('no', 'No')
    ], string='¿Tiene Moto?', default='no', tracking=True)

    marca_Moto_id = fields.Many2one('fundacupaz.moto.marca', string="Marca de la Moto", tracking=True)
    modelo_Moto_id = fields.Many2one('fundacupaz.moto.modelo',
                                     string="Modelo de la Moto",
                                     tracking=True)
    serial_vehiculo = fields.Char(string="Serial de Vehículo/Moto (IMEI/Chasis)", tracking=True)

