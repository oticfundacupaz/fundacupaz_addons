# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

# Modelo para Marcas de Moto
class FundacupazMotoMarca(models.Model):
    _name = "fundacupaz.moto.marca"
    _description = 'Marca de Moto'
    _order = 'name'

    name = fields.Char("Marca de la Moto", required=True)
    modelo_ids = fields.One2many(
        'fundacupaz.moto.modelo',
        'marca_id',
        string='Modelos'
    )