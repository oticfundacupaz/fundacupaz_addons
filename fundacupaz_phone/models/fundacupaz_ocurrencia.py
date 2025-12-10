# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class FundacupazOcurrencia(models.Model):
    _name = "fundacupaz.ocurrencia"
    _description = 'Ocurrencia o Incidencia de Cuadrante'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_ocurrencia desc, id desc'

    name = fields.Char(string='Incidencia N°', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('Nuevo'))

    # --- LÓGICA DEL BOTÓN (Aquí revisamos que esté perfecto) ---
    attachment_count = fields.Integer(string='N° Documentos', compute='_compute_attachment_count')

    def _compute_attachment_count(self):
        # Cuenta los adjuntos vinculados a este modelo y a este ID específico
        for record in self:
            count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'fundacupaz.ocurrencia'),
                ('res_id', '=', record.id)
            ])
            record.attachment_count = count

    def action_ver_adjuntos(self):
        self.ensure_one()
        return {
            'name': _('Datos de Incidencias'), # El título de la ventana que se abre
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'context': "{'default_res_model': '%s', 'default_res_id': %d}" % (self._name, self.id),
            'help': _('''<p class="o_view_nocontent_smiling_face">
                                Aún no se han generado reportes para esta incidencia.
                            </p>'''),
        }

    # Datos principales
    phone_id = fields.Many2one('fundacupaz.phone', string="Teléfono Reportante", required=True, tracking=True)
    fecha_ocurrencia = fields.Date(string="Fecha", required=True, tracking=True)
    hora_ocurrencia = fields.Float(string="Hora", required=True, tracking=True)

    cuadrante_id = fields.Many2one('fundacupaz.cuadrante', related='phone_id.cuadrantes', store=True, string="Cuadrante")
    estado_id = fields.Many2one('res.country.state', related='phone_id.estado', store=True, string="Estado")
    municipio_id = fields.Many2one('res.country.state.municipality', related='phone_id.municipio', store=True, string="Municipio")
    parroquia_del_telefono = fields.Char(related='phone_id.parroqui_comuna', store=True, string="Parroquia")
    circuito_comunal = fields.Char(related='cuadrante_id.circuito_comunal', store=True, string="Circuito Comunal")
    organo_seguridad = fields.Selection(related='phone_id.operadora', store=True, string="Operadora")

    organismo = fields.Selection(
        related='phone_id.organismo',
        store=True,
        string="Organismo de Seguridad",
        tracking=True
    )

    jefe_cuadrante_manual = fields.Char(string="Jefe Cuadrante (Manual)", tracking=True)
    detalle_incidencia = fields.Text(string="Detalles de los Hechos", tracking=True)

    estatus = fields.Selection(
        selection=[
            ('PENDIENTE', 'PENDIENTE'),
            ('EN PROCESO', 'EN PROCESO'),
            ('RESUELTO', 'RESUELTO')
        ],
        string="Estado de Incidencia",
        default='PENDIENTE',  # Valor inicial automático
        tracking=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fundacupaz.ocurrencia') or _('Nuevo')
        return super(FundacupazOcurrencia, self).create(vals)