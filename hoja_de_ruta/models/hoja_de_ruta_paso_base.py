from odoo import models, fields

class HojaDeRutaPasoBase(models.Model):
    _name = 'hoja.de.ruta.paso.base'
    _description = 'Pasos Base de la Hoja de Ruta'
    _order = 'name'

    name = fields.Char(string='Descripción del Paso', required=True, unique=True)
    # Puedes agregar más campos a este modelo si necesitas detalles adicionales
    # para cada paso base (ej., responsable por defecto, duración estimada, etc.)