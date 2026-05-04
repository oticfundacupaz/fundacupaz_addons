# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployeeDependent(models.Model):
    _name = 'hr.employee.dependent'
    _description = 'Empleado - Hijos Dependientes'

    name = fields.Char(string='Nombre', required=True)
    last_name = fields.Char(string='Apellido', required=True)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino'),
    ], string='Género', required=True)
    birthday = fields.Date(string='Fecha de nacimiento')
    age = fields.Integer(string='Edad', compute='_compute_age', store=False)
    employee_id = fields.Many2one('hr.employee', string='Empleado', ondelete='cascade')

    @api.depends('birthday')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if record.birthday:
                # Calcula la edad basada en si ya cumplió años este año o no
                age_calc = today.year - record.birthday.year - ((today.month, today.day) < (record.birthday.month, record.birthday.day))
                record.age = age_calc
            else:
                record.age = 0

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    dependent_ids = fields.One2many(
        'hr.employee.dependent', 'employee_id', string='Hijos (Detalle)'
    )
    sueldo = fields.Float(string='Sueldo (Remuneración Mensual)')
    service_start_date = fields.Date(string='Fecha de inicio de servicio')
    custom_status = fields.Selection([
        ('active', 'Activo'),
        ('inactive', 'Inactivo')
    ], string='Estatus', default='active')
    
    custom_resume_file = fields.Binary(string='Archivo PDF del Currículum', attachment=True)
    custom_resume_filename = fields.Char(string='Nombre del Archivo')

    @api.onchange('children')
    def _onchange_children(self):
        """
        Activa la creación/eliminación dinámica de campos
        para la información de los hijos dependientes de la cantidad ingresada.
        """
        warning_res = False
        for record in self:
            target_count = record.children or 0
            
            if target_count > 7:
                target_count = 7
                record.children = 7
                warning_res = True

            current_count = len(record.dependent_ids)

            if target_count > current_count:
                # Add empty records
                extra_lines = target_count - current_count
                commands = [(0, 0, {}) for _ in range(extra_lines)]
                record.dependent_ids = commands
            elif target_count < current_count:
                # Remove extra records from the end
                record.dependent_ids = record.dependent_ids[:target_count]
                
        if warning_res:
            return {
                'warning': {
                    'title': 'Límite excedido',
                    'message': 'Para evitar la creación masiva de casillas por accidente, el sistema está limitado a un máximo de 7 hijos.'
                }
            }
