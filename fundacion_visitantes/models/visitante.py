# -*- coding: utf-8 -*-
from odoo import models, fields

class Visitante(models.Model):
    _name = 'fundacion.visitante'
    _description = 'Registro de Visitantes'

    name = fields.Char(string='Nombre Completo', required=True)
    identification_number = fields.Char(string='Cédula / ID', required=True, copy=False)
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Correo Electrónico')

    image_1920 = fields.Image(string="Foto del Visitante", help="Foto tomada con la webcam o cargada desde un archivo.")

    # Para que Odoo muestre el nombre del visitante en las relaciones
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, f"{rec.name} ({rec.identification_number})"))
        return result