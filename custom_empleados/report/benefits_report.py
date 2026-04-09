# -*- coding: utf-8 -*-

from odoo import models, api

class BenefitsReportDocToys(models.AbstractModel):
    _name = 'report.custom_empleados.report_employee_toy_template'
    _description = 'Abstract Model for Benefits Report Engine'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data is None:
            data = {}

        report_type = data.get('report_type', 'toys')
        report_title = data.get('report_name_title', 'Reporte de Juguetes')
        min_age, max_age = 0, 13

        # Buscamos todos los empleados activos
        employees = self.env['hr.employee'].search([])

        # Extraemos todos los hijos y los filtramos por rango, ordenándolos por edad
        all_children = employees.mapped('dependent_ids').filtered(lambda c: min_age <= c.age <= max_age)
        all_children_sorted = all_children.sorted(key=lambda c: c.age)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': all_children_sorted,
            'report_title': report_title,
            'min_age': min_age,
            'max_age': max_age,
        }

class BenefitsReportDocSchool(models.AbstractModel):
    _name = 'report.custom_empleados.report_employee_school_template'
    _description = 'Abstract Model for Benefits Report Engine - School'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data is None:
            data = {}

        report_type = data.get('report_type', 'school')
        report_title = data.get('report_name_title', 'Reporte de Útiles Escolares')
        min_age, max_age = 3, 17

        # Buscamos todos los empleados activos
        employees = self.env['hr.employee'].search([])

        # Extraemos todos los hijos y los filtramos por rango, ordenándolos por edad
        all_children = employees.mapped('dependent_ids').filtered(lambda c: min_age <= c.age <= max_age)
        all_children_sorted = all_children.sorted(key=lambda c: c.age)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': all_children_sorted,
            'report_title': report_title,
            'min_age': min_age,
            'max_age': max_age,
        }
