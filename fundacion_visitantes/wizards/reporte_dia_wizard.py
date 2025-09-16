# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, time


class VisitaReporteDiaWizard(models.TransientModel):
    _name = 'fundacion.visita.reporte.dia.wizard'
    _description = 'Asistente para Reporte de Visitas por Día'

    fecha_reporte = fields.Date(string="Fecha del Reporte", required=True, default=fields.Date.context_today)

    def action_imprimir_reporte(self):
        # Establece el rango de búsqueda para el día completo
        fecha = self.fecha_reporte
        fecha_inicio = datetime.combine(fecha, time.min)
        fecha_fin = datetime.combine(fecha, time.max)

        # Busca todos los registros de 'fundacion.visita' en esa fecha
        visitas_ids = self.env['fundacion.visita'].search([
            ('entry_date', '>=', fecha_inicio),
            ('entry_date', '<=', fecha_fin)
        ])

        if not visitas_ids:
            raise UserError("No se encontraron visitas registradas para la fecha seleccionada.")

        # Preparamos los datos a enviar al reporte
        data = {
            'fecha_reporte': self.fecha_reporte,
            'nombre_usuario': self.env.user.name,
        }

        # Llama a la acción del reporte, enviando el diccionario de datos
        return self.env.ref('fundacion_visitantes.action_report_visitas_por_dia').report_action(
            docids=visitas_ids,
            data=data,
        )