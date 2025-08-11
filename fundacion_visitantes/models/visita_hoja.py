# -*- coding: utf-8 -*-
from odoo import models, fields, api


class VisitaHoja(models.Model):
    _name = 'fundacion.visita.hoja'
    _description = 'Hoja de Registro de Visitas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('fundacion.visita.hoja'))
    date = fields.Date(string='Fecha', default=fields.Date.today, required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Validado'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)

    visita_ids = fields.One2many('fundacion.visita', 'hoja_id', string='Visitas')



    def action_validate(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_reset_draft(self):
        self.state = 'draft'

    def action_view_visitas(self):
        self.ensure_one()
        return {
            'name': 'Visitas',
            'type': 'ir.actions.act_window',
            'res_model': 'fundacion.visita',
            'view_mode': 'list,form',
            'domain': [('hoja_id', '=', self.id)],
            'context': {'default_hoja_id': self.id}
        }