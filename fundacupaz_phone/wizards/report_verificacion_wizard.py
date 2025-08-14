# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, time, timedelta



class ReportVerificacionWizard(models.TransientModel):
    _name = 'fundacupaz.phone.report.wizard'
    _description = 'Wizard para Reporte de Verificación Telefónica'

    # Campo para que el usuario seleccione el turno
    turno_seleccion = fields.Selection(
        selection=[
            ('turno_1', 'Turno de 00:00 a 11:00'),
            ('turno_2', 'Turno de 11:01 a 23:59'),
            ('turno_3', 'Día Completo (00:00 a 23:59)')
        ],
        string="Seleccionar Turno",
        required=True,
        default='turno_3'
    )

    # Campos para mostrar el rango de fechas (no editables)
    fecha_inicio = fields.Datetime(string="Fecha de Inicio", readonly=True, compute='_compute_fechas')
    fecha_fin = fields.Datetime(string="Fecha de Fin", readonly=True, compute='_compute_fechas')

    @api.depends('turno_seleccion')
    def _compute_fechas(self):
        for wizard in self:
            hoy = datetime.now().date()
            sumar_horas = timedelta(hours=4)

            if wizard.turno_seleccion == 'turno_1':
                wizard.fecha_inicio = datetime.combine(hoy, time.min) + sumar_horas
                wizard.fecha_fin = datetime.combine(hoy, time(11, 0, 0)) + sumar_horas
            elif wizard.turno_seleccion == 'turno_2':
                wizard.fecha_inicio = datetime.combine(hoy, time(11, 0, 1)) + sumar_horas
                wizard.fecha_fin = datetime.combine(hoy, time.max) + sumar_horas
            else:  # turno_3 (día completo)
                wizard.fecha_inicio = datetime.combine(hoy, time.min) + sumar_horas
                wizard.fecha_fin = datetime.combine(hoy, time.max) + sumar_horas

    def action_print_report(self):
        """
        Esta función se ejecuta al presionar el botón 'Imprimir'.
        Convierte los registros en diccionarios antes de pasarlos al reporte.
        """
        self.ensure_one()

        domain = [
            ('telf_corresponde', '=', 'no'),
            ('fecha_revision_time', '>=', self.fecha_inicio),
            ('fecha_revision_time', '<=', self.fecha_fin)
        ]
        telefonos_a_reportar = self.env['fundacupaz.phone'].search(domain)

        if not telefonos_a_reportar:
            raise UserError(_("No se encontraron registros para los criterios seleccionados."))

        # -- LÓGICA DE AGRUPACIÓN Y CONVERSIÓN A DICCIONARIOS --
        telefonos_agrupados = {}
        for phone in telefonos_a_reportar:
            estado_nombre = phone.estado.name if phone.estado else 'Sin Estado'
            if estado_nombre not in telefonos_agrupados:
                telefonos_agrupados[estado_nombre] = []

            if phone.fecha_revision_time:
                fecha_ajustada = phone.fecha_revision_time - timedelta(hours=4)
                fecha_modificacion_formateada = fecha_ajustada.strftime('%H:%M')
            else:
                fecha_modificacion_formateada = 'N/A'

            phone_dict = {
                'number_phone': phone.number_phone,
                'operadora': phone.operadora,
                'municipio': phone.municipio.name if phone.municipio else 'N/A',
                'cuadrantes': phone.cuadrantes.name if phone.cuadrantes else 'N/A',
                'motivo_seleccionado': phone.motivo_seleccionado,
                'motivo_otros_observaciones': phone.motivo_otros_observaciones,
                'estatus': phone.estatus,
                'fecha_revision_time': fecha_modificacion_formateada,
            }
            telefonos_agrupados[estado_nombre].append(phone_dict)

        lista_telefonos_agrupados = []
        for estado, records in telefonos_agrupados.items():
            lista_telefonos_agrupados.append({'estado': estado, 'records': records})
        # -- FIN DE LA LÓGICA --

        return self.env.ref('fundacupaz_phone.action_report_fundacupaz_verificacion').report_action(
            self, data={'telefonos_agrupados': lista_telefonos_agrupados})