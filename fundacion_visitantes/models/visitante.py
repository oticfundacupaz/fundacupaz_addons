# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Visitante(models.Model):
    _name = 'fundacion.visitante'
    _description = 'Registro de Visitantes'

    name = fields.Char(string='Nombre Completo', required=True)
    identification_number = fields.Char(string='Cédula / ID', required=True, copy=False)
    phone = fields.Char(string='Teléfono', required=True)

    image_1920 = fields.Image(string="Foto del Visitante", help="Foto tomada con la webcam o cargada desde un archivo.")

    # Para que Odoo muestre el nombre del visitante en las relaciones
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, f"{rec.name} ({rec.identification_number})"))
        return result

    @api.constrains('identification_number', 'phone')
    def _check_numeric_and_length(self):
        for rec in self:
            if rec.identification_number and not rec.identification_number.isdigit():
                raise ValidationError("El campo 'Cédula / ID' solo debe contener números.")
            if rec.phone:
                if not rec.phone.isdigit():
                    raise ValidationError("El campo 'Teléfono' solo debe contener números.")
                if len(rec.phone) != 11:
                    raise ValidationError("El campo 'Teléfono' debe tener exactamente 11 dígitos.")

