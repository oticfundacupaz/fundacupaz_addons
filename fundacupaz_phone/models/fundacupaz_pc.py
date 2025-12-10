# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FundacupazPC(models.Model):
    _name = "fundacupaz.pc"
    _inherit = "mail.thread"

    name = fields.Many2one('product.template', domain="[('categ_id', '=', 'Equipos Computación')]", string="Nombre PC")
    serial = fields.Many2one('stock.lot', domain="[('product_id', '=', name)]", string="Serial")
    conexion_red = fields.Selection(selection=[('PUNTO', 'PUNTO'), ('WIFI', 'WIFI')], string='Red')
    bien_mueble = fields.Char("Bien Mueble")
    mac = fields.Char("Mac")
    sistema_operativo = fields.Char("Sistema Operativo")
    memoria_ram = fields.Char("Memoria Ram")
    procesador = fields.Char("Procesador")
    disco_duro = fields.Char("Disco Duro")
    ip = fields.Char("IP")
    ente = fields.Many2one('fundacupaz.ente', string="Ente Asignado")
    persona_asignada = fields.Many2one('res.partner', domain="[('is_company', '!=','true')]", string="Persona Asignada")
    estatus = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('OPERATIVA', 'OPERATIVA'),
            ('INOPERATIVA', 'INOPERATIVA'),
            ('DESINCORPORADA', 'DESINCORPORADA')
        ], string='Estatus')
    observaciones = fields.Char("Observaciones")


    @api.constrains('name', 'serial')
    def _check_pc_serial(self):
        for record in self:
            existing_records = record.env['fundacupaz.pc'].search([('name', '=', record.name.id), ('serial', '=', record.serial.id), ('id', '!=', record.id)])
        if existing_records:
            raise ValidationError("Los valores del nombre del producto y el serial deben ser únicos.")