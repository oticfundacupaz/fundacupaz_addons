# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AsistenciaEntrada(models.Model):
    _name = 'asistencia.entrada'
    _description = 'Asistencia de Entrada'
    _order = 'fecha desc, hora desc'
    _rec_name = 'nombre_empleado'

    cedula = fields.Char(string='Cédula', required=True, index=True)
    fecha = fields.Date(string='Fecha', required=True)
    hora = fields.Char(string='Hora', required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        ondelete='set null',
    )
    nombre_empleado = fields.Char(
        string='Nombre',
        store=True,
    )
    department_id = fields.Many2one(
        related='employee_id.department_id',
        string='Departamento',
        store=True,
    )
    telefono_privado = fields.Char(
        related='employee_id.private_phone',
        string='Teléfono Privado',
        store=True,
    )
    custom_status = fields.Selection(
        related='employee_id.custom_status',
        string='Estatus',
        store=True,
    )

    @api.model
    def _buscar_empleado_por_cedula(self, cedula):
        """Busca un empleado en hr.employee usando el campo identificacion_id."""
        pass
