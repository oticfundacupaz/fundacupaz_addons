# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, time


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
        """Calcula las fechas de inicio y fin basadas en el turno seleccionado."""
        for wizard in self:
            hoy = datetime.now().date()
            if wizard.turno_seleccion == 'turno_1':
                wizard.fecha_inicio = datetime.combine(hoy, time.min)  # 00:00:00
                wizard.fecha_fin = datetime.combine(hoy, time(11, 0, 0))  # 11:00:00
            elif wizard.turno_seleccion == 'turno_2':
                wizard.fecha_inicio = datetime.combine(hoy, time(11, 0, 1))  # 11:00:01
                wizard.fecha_fin = datetime.combine(hoy, time.max)  # 23:59:59
            else:  # turno_3 o por defecto
                wizard.fecha_inicio = datetime.combine(hoy, time.min)
                wizard.fecha_fin = datetime.combine(hoy, time.max)

    def action_print_report(self):
        """
        Esta función se ejecuta al presionar el botón 'Imprimir'.
        Convierte los registros en diccionarios antes de pasarlos al reporte.
        """
        self.ensure_one()

        domain = [
            ('telf_corresponde', '=', 'no'),
            ('write_date', '>=', self.fecha_inicio),
            ('write_date', '<=', self.fecha_fin)
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

            phone_dict = {
                'number_phone': phone.number_phone,
                'operadora': phone.operadora,
                'cuadrantes': phone.cuadrantes.name,
                'motivo_seleccionado': phone.motivo_seleccionado,
                'motivo_otros_observaciones': phone.motivo_otros_observaciones,
                'estatus': phone.estatus
            }
            telefonos_agrupados[estado_nombre].append(phone_dict)

        lista_telefonos_agrupados = []
        for estado, records in telefonos_agrupados.items():
            lista_telefonos_agrupados.append({'estado': estado, 'records': records})
        # -- FIN DE LA LÓGICA --

        return self.env.ref('fundacupaz_phone.action_report_fundacupaz_verificacion').report_action(
            self, data={'telefonos_agrupados': lista_telefonos_agrupados})