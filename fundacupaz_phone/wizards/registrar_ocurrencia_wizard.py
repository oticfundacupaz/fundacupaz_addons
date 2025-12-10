# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError  # Importante importar esto


class RegistrarOcurrenciaWizard(models.TransientModel):
    _name = 'fundacupaz.registrar.ocurrencia.wizard'
    _description = 'Asistente para Registrar Ocurrencia'

    # --- CAMPOS ---
    numero_telefono_input = fields.Char(string="Número de Teléfono", required=True)
    phone_record_id = fields.Many2one('fundacupaz.phone', string="Registro Encontrado")
    fecha_ocurrencia = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    hora_ocurrencia = fields.Float(string="Hora", required=True,
                                   default=lambda self: fields.Datetime.now().hour + (
                                           fields.Datetime.now().minute / 60.0))

    # Campos relacionados
    estado_id = fields.Many2one('res.country.state', related='phone_record_id.estado', readonly=True)
    municipio_id = fields.Many2one('res.country.state.municipality', related='phone_record_id.municipio', readonly=True)
    parroquia_del_telefono = fields.Char(related='phone_record_id.parroqui_comuna', readonly=True)
    circuito_comunal = fields.Char(related='phone_record_id.cuadrantes.circuito_comunal', readonly=True)
    organo_seguridad = fields.Selection(related='phone_record_id.operadora', readonly=True)

    organismo = fields.Selection(related='phone_record_id.organismo', readonly=True, string="Organismo")

    estatus_telefono = fields.Selection(related='phone_record_id.estatus', readonly=True, string="Estado del Teléfono")

    estatus_incidencia = fields.Selection([
        ('PENDIENTE', 'PENDIENTE'),
        ('EN PROCESO', 'EN PROCESO'),
        ('RESUELTO', 'RESUELTO')
    ], string="Estado de Incidencia", default='PENDIENTE', required=True)

    # Campos manuales
    jefe_cuadrante_manual = fields.Char(string="Jefe Cuadrante (Manual)")
    detalle_incidencia = fields.Html(string="Detalle de la Incidencia")

    @api.onchange('numero_telefono_input')
    def _onchange_numero_telefono(self):
        if self.numero_telefono_input:
            # Buscamos el teléfono
            telefono = self.env['fundacupaz.phone'].search([
                ('number_phone', '=', self.numero_telefono_input)
            ], order='id desc', limit=1)

            if telefono:
                self.phone_record_id = telefono.id
                if telefono.cuadrantes and telefono.cuadrantes.jefe_cuadrante:
                    self.jefe_cuadrante_manual = telefono.cuadrantes.jefe_cuadrante.name
                else:
                    self.jefe_cuadrante_manual = "No asignado"
            else:
                self.phone_record_id = False
                self.jefe_cuadrante_manual = "Número no registrado"

    def action_registrar_e_imprimir(self):
        self.ensure_one()

        # VALIDACIÓN DE SEGURIDAD
        if not self.phone_record_id:
            raise ValidationError(
                _("No se ha encontrado un registro de teléfono válido para el número ingresado. Verifique que el número exista en la base de datos de Teléfonos."))

        vals = {
            'phone_id': self.phone_record_id.id,
            'fecha_ocurrencia': self.fecha_ocurrencia,
            'hora_ocurrencia': self.hora_ocurrencia,
            'jefe_cuadrante_manual': self.jefe_cuadrante_manual,
            'detalle_incidencia': self.detalle_incidencia,
        }

        # 1. Crear la incidencia
        nueva_ocurrencia = self.env['fundacupaz.ocurrencia'].create(vals)

        # 2. Devolver la acción para imprimir el PDF directamente (CORRECCIÓN CLAVE)
        return self.env.ref('fundacupaz_phone.action_report_ocurrencia').report_action(nueva_ocurrencia)