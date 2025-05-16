from odoo import models, fields, api


class HojaDeRutaLinea(models.Model):
    _name = 'hoja_de_ruta.linea'
    _description = 'Línea de Seguimiento de la Hoja de Ruta'
    _order = 'sequence, id'  # Para mantener el orden de los pasos

    hoja_de_ruta_id = fields.Many2one('hoja.de.ruta', string='Hoja de Ruta', required=True, ondelete='cascade')
    paso_id = fields.Many2one('hoja.de.ruta.paso.base', string='Descripción del Paso', required=True, tracking=True)
    completado = fields.Boolean(string='Completado', default=False, tracking=True)
    sequence = fields.Integer(string='Secuencia', default=10)
    fecha = fields.Date(string='Fecha', tracking=True)
    observaciones = fields.Text(string='Observaciones', tracking=True)
    # Aquí podrías agregar más campos si los necesitas en el futuro
    # responsable_id = fields.Many2one('res.users', string='Responsable')
    # documentos_ids = fields.Many2many('ir.attachment', string='Documentos')