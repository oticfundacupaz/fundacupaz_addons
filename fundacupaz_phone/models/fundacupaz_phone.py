# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazPhone(models.Model):
    _name = "fundacupaz.phone"
    _inherit = "mail.thread"

    number_phone = fields.Char("Número Telefono")
    marca_phone = fields.Char("Marca")
    modelo_phone = fields.Char("Modelo")
    imei_phone = fields.Char("IMEI")
    number_phone = fields.Char("Numero Telefono")
    operadora = fields.Selection(
        selection=[
            ('MOVILNET', 'MOVILNET'),
            ('MOVISTAR', 'MOVISTAR'),
            ('DIGITEL', 'DIGITEL')
        ],
    string='Operadora')
    planes = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('MOVILNET EMPRENDE 10', 'MOVILNET EMPRENDE 10'),
            ('MOVISTAR PLUS 25 GB', 'MOVISTAR PLUS 25 GB'),
            ('MOVISTAR PLUS 10 GB', 'MOVISTAR PLUS 10 GB'),
            ('DIGITEL INTELIGENTE PLUS 1.1GB', 'DIGITEL INTELIGENTE PLUS 1.1GB'),
            ('DIGITEL INTELIGENTE PLUS 2GB', 'DIGITEL INTELIGENTE PLUS 2GB'),
            ('DIGITEL INTELIGENTE PLUS 6GB', 'DIGITEL INTELIGENTE PLUS 6GB'),
            ('DIGITEL INTELIGENTE PLUS 30GB', 'DIGITEL INTELIGENTE PLUS 30GB')
        ],
        string='Planes')
    ente = fields.Many2one('fundacupaz.ente',string="Ente Asignado")
    persona_asignada = fields.Many2one('res.partner',domain="[('is_company', '!=','true')]",string="Persona Asignada" )
    estatus = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('ACTIVA', 'ACTIVA'),
            ('INACTIVA', 'INACTIVA'),
            ('SUSPENDIDA', 'SUSPENDIDA')
        ],
    string='Estatus', default=False)

    estado = fields.Many2one('res.country.state',domain="[('country_id.name','=','Venezuela')]", string="Estado")
    municipio = fields.Many2one('res.country.state.municipality' ,domain="[('state_id','=', estado)]", string="Municipio")
    cuadrante = fields.Char("Cuadrante")
    observaciones = fields.Char("Observaciones")

    @api.constrains('estado')
    def _check_estado_comisionado(self):
        for record in self:
            user_estado_id = self.env.user.estado_comisionado.id if self.env.user.estado_comisionado else False
            if record.estado.id != user_estado_id:
                raise ValidationError("El estado seleccionado no coincide con el estado asignado al comisionado actual.")