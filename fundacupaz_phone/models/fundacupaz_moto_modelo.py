# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


# Modelo para Modelos de Moto
class FundacupazMotoModelo(models.Model):
    _name = "fundacupaz.moto.modelo"
    _description = 'Modelo de Moto'
    _order = 'name'

    name = fields.Char("Modelo de la Moto", required=True)
    marca_id = fields.Many2one(
        'fundacupaz.moto.marca',
        string='Marca',
        required=True,
        ondelete='cascade'
    )

    # Restricción para asegurar que el nombre del modelo sea único por marca
    _sql_constraints = [
        ('name_marca_uniq', 'unique (name, marca_id)', 'El nombre del modelo debe ser único por marca.')
    ]