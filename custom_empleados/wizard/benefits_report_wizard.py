# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BenefitsReportWizard(models.TransientModel):
    _name = 'benefits.report.wizard'
    _description = 'Asistente de Reporte de Beneficios'

    report_type = fields.Selection([
        ('toys', 'Entrega de Juguetes (0 a 13 años)'),
        ('school', 'Útiles Escolares (3 a 17 años)'),
    ], string='Tipo de Beneficio', required=True, default='toys')

    def action_print_report(self):
        """
        Dispara el renderizado del reporte en PDF pasándole el rango de edad.
        """
        data = {
            'report_type': self.report_type,
            'report_name_title': dict(self._fields['report_type'].selection).get(self.report_type),
        }
        
        if self.report_type == 'toys':
            action = self.env.ref('custom_empleados.action_report_employee_toy').report_action(self, data=data)
        else:
            action = self.env.ref('custom_empleados.action_report_employee_school').report_action(self, data=data)
            
        return action
