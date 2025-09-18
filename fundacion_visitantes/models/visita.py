# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class Visita(models.Model):
    _name = 'fundacion.visita'
    _description = 'Visitas Diarias'
    _order = 'hoja_id asc, entry_date desc'

    hoja_id = fields.Many2one('fundacion.visita.hoja', string='Hoja de Visita', required=True, ondelete='cascade')

    visitor_id = fields.Many2one('fundacion.visitante', string='Visitante', ondelete='restrict')

    name = fields.Char(string='Nombre Completo')
    identification_number = fields.Char(string='Cédula / ID')
    phone = fields.Char(string='Teléfono')
    origen = fields.Char(string='Origen')
    visit_purpose = fields.Text(string='Motivo de la Visita', required=True)
    destination_person = fields.Selection(
        selection=[
            ('PRE', 'PRESIDENCIA'),
            ('RRHH', 'RECURSOS HUMANOS'),
            ('COMISION', 'COMISION'),
            ('SALASI', 'SALA SITUACIONAL'),
            ('SC', 'SALA DE CONFERENCIA'),
            ('PROYECTOS', 'PROYECTOS'),
            ('TEC', 'TECNOLOGIA'),
            ('FIN', 'FINANSAS'),
            ('SER', 'SERVICIOS GENERALES'),
            ('COC', 'COCINA'),
            ('AUD', 'AUDITORIA'),
            ('REC', 'RECEPCION'),
            ('ALM', 'ALMACEN')
        ], string='Se dirige a')

    entry_date = fields.Datetime(string='Hora de Entrada', default=fields.Datetime.now, readonly=True)
    exit_date = fields.Datetime(string='Hora de Salida')

    @api.onchange('visitor_id')
    def _onchange_visitor_id(self):
        if self.visitor_id:
            self.name = self.visitor_id.name
            self.identification_number = self.visitor_id.identification_number
            self.phone = self.visitor_id.phone
        else:
            self.name = False
            self.identification_number = False
            self.phone = False

    @api.constrains('entry_date', 'exit_date')
    def _check_exit_date_after_entry_date(self):
        for record in self:
            if record.entry_date and record.exit_date:
                # La diferencia de tiempo debe ser mayor a 60 segundos (1 minuto)
                if (record.exit_date - record.entry_date).total_seconds() < 60:
                    raise ValidationError("La hora de salida debe ser al menos un minuto después de la hora de entrada.")

    @api.model
    def create(self, vals):
        # Si se selecciona un visitante existente, usamos sus datos para rellenar los campos
        if vals.get('visitor_id'):
            visitor = self.env['fundacion.visitante'].browse(vals['visitor_id'])
            vals['name'] = visitor.name
            vals['identification_number'] = visitor.identification_number
            vals['phone'] = visitor.phone
        # Si no hay visitante, creamos uno nuevo
        elif vals.get('identification_number'):
            existing_visitor = self.env['fundacion.visitante'].search(
                [('identification_number', '=', vals['identification_number'])], limit=1)
            if not existing_visitor:
                vals['visitor_id'] = self.env['fundacion.visitante'].create({
                    'name': vals.get('name'),
                    'identification_number': vals.get('identification_number'),
                    'phone': vals.get('phone'),
                }).id
            else:
                vals['visitor_id'] = existing_visitor.id

        return super(Visita, self).create(vals)