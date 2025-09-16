# -*- coding: utf-8 -*-
import base64
import io
from odoo import models, fields, api

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class PhoneReportWizard(models.TransientModel):
    _name = 'fundacupaz.phone.report.wizard'
    _description = 'Asistente para Reportes de Teléfonos'

    def _get_phone_ids(self):
        # Obtiene los IDs de los teléfonos seleccionados o todos si no hay selección
        return self.env.context.get('active_ids', self.env['fundacupaz.phone'].search([]).ids)

    def action_export_excel(self):
        """Genera y descarga el archivo Excel."""
        if not xlsxwriter:
            # Puedes añadir aquí una advertencia si la librería no está instalada
            return

        phone_ids = self._get_phone_ids()
        phones = self.env['fundacupaz.phone'].browse(phone_ids)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Reporte de Teléfonos')

        # Estilos y encabezados
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D3D3D3'})
        headers = ['Número', 'Operadora', 'Estatus', 'Plan', 'Ente Asignado', 'Estado', 'Municipio']
        for i, header in enumerate(headers):
            sheet.write(0, i, header, header_format)

        # Escribir datos
        row = 1
        for phone in phones:
            sheet.write(row, 0, phone.number_phone or '')
            sheet.write(row, 1, phone.operadora or '')
            sheet.write(row, 2, phone.estatus or '')
            sheet.write(row, 3, phone.plan_id.name or '')
            sheet.write(row, 4, phone.ente.name or '')
            sheet.write(row, 5, phone.estado.name or '')
            sheet.write(row, 6, phone.municipio.name or '')
            row += 1

        workbook.close()
        output.seek(0)

        file_data = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Reporte_Telefonos.xlsx',
            'datas': file_data,
            'type': 'binary',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_export_pdf(self):
        """Llama a la acción de reporte para generar el PDF."""
        phone_ids = self._get_phone_ids()
        phones = self.env['fundacupaz.phone'].browse(phone_ids)

        # Llama al reporte PDF definido en XML
        return self.env.ref('fundacupaz_dashboard.action_report_fundacupaz_phone').report_action(phones)