# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReporteAsistenciaWizard(models.TransientModel):
    _name = 'reporte.asistencia.wizard'
    _description = 'Wizard para generar reporte de asistencias'

    fecha_desde = fields.Date(
        string='Fecha Desde',
        required=True,
        default=fields.Date.context_today,
    )
    fecha_hasta = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.context_today,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Departamento',
        help='Dejar vacío para incluir todos los departamentos',
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Empleados',
        help='Dejar vacío para incluir todos los empleados del período',
    )
    agrupar_por_departamento = fields.Boolean(
        string='Agrupar por Departamento',
        default=True,
    )

    def _get_domain(self):
        """Construye el dominio de búsqueda según los filtros."""
        domain = [
            ('fecha', '>=', self.fecha_desde),
            ('fecha', '<=', self.fecha_hasta),
        ]
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        return domain

    def action_generar_reporte(self):
        """Genera el reporte PDF."""
        domain = self._get_domain()
        asistencias = self.env['asistencia.entrada'].search(
            domain, order='department_id, nombre_empleado, fecha, hora'
        )
        return self.env.ref(
            'fundacupaz_asistencias.action_reporte_asistencias'
        ).report_action(self, data={})

    def get_report_data(self):
        """Datos que serán pasados al template QWeb."""
        domain = self._get_domain()
        asistencias = self.env['asistencia.entrada'].search(
            domain, order='department_id, nombre_empleado, fecha, hora'
        )

        # Agrupar por departamento
        grupos = {}
        for a in asistencias:
            dept_name = a.department_id.name if a.department_id else 'Sin Departamento'
            if dept_name not in grupos:
                grupos[dept_name] = []
            grupos[dept_name].append(a)

        grouped_records = [
            {'nombre': k, 'asistencias': v, 'total': len(v)}
            for k, v in sorted(grupos.items())
        ]

        return {
            'asistencias': asistencias,
            'grouped_records': grouped_records,
            'total_asistencias': len(asistencias),
            'agrupar': self.agrupar_por_departamento,
            'fecha_desde': self.fecha_desde.strftime('%d/%m/%Y'),
            'fecha_hasta': self.fecha_hasta.strftime('%d/%m/%Y'),
            'department_name': self.department_id.name if self.department_id else 'Todos los departamentos',
        }
