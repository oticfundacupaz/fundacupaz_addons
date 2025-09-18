# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VisitaReportWizard(models.TransientModel):
    _name = 'fundacion.visita.report.wizard'
    _description = 'Asistente para Reporte de Visitas por Destino'

    date_filter = fields.Date(string="Fecha del Reporte", required=True, default=fields.Date.context_today)
    destination_person = fields.Selection(
        selection=[
            ('PRE', 'PRESIDENCIA'),
            ('RRHH', 'RECURSOS HUMANOS'),
            ('COMISION', 'COMISION'),
            ('SALASI', 'SALA SITUACIONAL'),
            ('SC', 'SALA DE CONFERENCIA'),
            ('PROYECTOS', 'PROYECTOS'),
            ('TEC', 'TECNOLOGIA'),
            ('FIN', 'FINANSAS'),
            ('SER', 'SERVICIOS GENERALES'),
            ('COC', 'COCINA'),
            ('AUD', 'AUDITORIA'),
            ('REC', 'RECEPCION'),
            ('ALM', 'ALMACEN')
        ], string='Se dirige a', required=True)

    def action_print_report(self):
        """
        Esta función recolecta los datos del wizard, busca las visitas que coinciden
        y llama a la acción de reporte para generar el PDF.
        """
        self.ensure_one()
        # Creamos el dominio de búsqueda
        domain = [
            # La fecha de entrada debe estar en el día seleccionado
            ('entry_date', '>=', self.date_filter),
            ('entry_date', '<', fields.Date.add(self.date_filter, days=1)),
            # El destino debe ser el seleccionado en el wizard
            ('destination_person', '=', self.destination_person),
        ]
        visitas = self.env['fundacion.visita'].search(domain)

        if not visitas:
            raise ValidationError("No se encontraron visitas para los filtros seleccionados.")

        # Llamamos a la acción del reporte y le pasamos los registros encontrados
        return self.env.ref('fundacion_visitantes.action_report_visitas_por_destino').report_action(visitas)