from odoo import models, fields, api


class HojaDeRuta(models.Model):
    _name = 'hoja.de.ruta'
    _description = 'Hoja de Ruta'
    _inherit = "mail.thread"

    name = fields.Char(string='Número de Proceso', required=True, tracking=True)
    correlativo = fields.Char(string='Correlativo', required=True, copy=False, readonly=True, default='Nuevo', tracking=True)
    objeto = fields.Text(string='Objeto', tracking=True)
    fecha_inicio = fields.Date(string='Fecha de Inicio', tracking=True)
    fecha_fin_prevista = fields.Date(string='Fecha Fin Prevista', tracking=True)

    institucion = fields.Selection([
        ('fispol', 'FISPOL'),
        ('fundacupaz', 'FUNDACUPAZ'),
        ('ministerio', 'Ministerio Interior, Justicia y Paz'),
    ], string='Institución', tracking=True)

    nombre_proveedor = fields.Many2one('res.partner', string='Nombre del Proveedor', tracking=True)

    lineas_ids = fields.One2many('hoja_de_ruta.linea', 'hoja_de_ruta_id', string='Seguimiento del Proceso')

    porcentaje_progreso = fields.Integer(string='Progreso', compute='_compute_porcentaje_progreso', store=True)

    estado = fields.Selection([
        ('por_ejecutar', 'Por Ejecutar'),
        ('en_ejecucion', 'En Ejecución'),
        ('ejecutada', 'Ejecutada'),
        ('cancelada', 'Cancelada'),
    ], string='Estado', default='por_ejecutar', tracking=True, compute='_compute_estado', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('correlativo', 'Nuevo') == 'Nuevo':
                vals['correlativo'] = self.env['ir.sequence'].next_by_code('hoja.de.ruta.correlativo') or 'Nuevo'
        return super().create(vals_list)

    @api.depends('lineas_ids.completado')
    def _compute_porcentaje_progreso(self):
        for record in self:
            total_lineas = len(record.lineas_ids)
            lineas_completadas = sum(1 for linea in record.lineas_ids if linea.completado)
            if total_lineas > 0:
                record.porcentaje_progreso = int((lineas_completadas / total_lineas) * 100)
            else:
                record.porcentaje_progreso = 0

    @api.depends('lineas_ids.completado')
    def _compute_estado(self):
        for record in self:
            if not record.lineas_ids:
                record.estado = 'por_ejecutar'
            elif all(linea.completado for linea in record.lineas_ids):
                record.estado = 'ejecutada'
            elif any(linea.completado for linea in record.lineas_ids):
                record.estado = 'en_ejecucion'
            else:
                record.estado = 'por_ejecutar'

    def action_view_progress(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Progreso de la Hoja de Ruta',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }