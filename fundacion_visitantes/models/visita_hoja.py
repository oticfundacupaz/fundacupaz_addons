# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class VisitaHoja(models.Model):
    _name = 'fundacion.visita.hoja'
    _description = 'Hoja de Registro de Visitas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Referencia', required=False, copy=False, readonly=True)
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
        action = self.env.ref('fundacion_visitantes.fundacion_visita_action').read()[0]
        action['domain'] = [('hoja_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fundacion.visita.hoja') or _('New')

        result = super(VisitaHoja, self).create(vals)
        return result