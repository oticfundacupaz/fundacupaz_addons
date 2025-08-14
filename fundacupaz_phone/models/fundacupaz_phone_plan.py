# -*- coding: utf-8 -*-
from odoo import models, fields

class FundacupazPhonePlan(models.Model):
    _name = "fundacupaz.phone.plan"
    _description = 'Registro de Teléfonos Fundacupaz'
    _order = "operadora, name"

    name = fields.Char("Nombre del Plan", required=True)

    operadora = fields.Selection(
        selection=[
        ('MOVISTAR', 'MOVISTAR'),
        ('MOVILNET', 'MOVILNET'),
        ('DIGITEL', 'DIGITEL')
    ],
     string='Operadora', required=True, tracking=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.operadora}] {record.name}"