# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazPhone(models.Model):
    _name = "fundacupaz.phone"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Registro de Teléfonos'

    number_phone = fields.Char("Número Telefono", tracking=True, size=11)
    marca_phone = fields.Char("Marca", tracking=True)
    modelo_phone = fields.Char("Modelo", tracking=True)
    imei_phone = fields.Char("IMEI", tracking=True)

    # --- CAMBIO 1: Modificar el campo 'operadora' ---
    operadora = fields.Selection(
        selection=[
            ('MOVILNET', 'MOVILNET'),
            ('MOVISTAR', 'MOVISTAR'),
            ('DIGITEL', 'DIGITEL')
        ],
        string='Operadora',
        tracking=True,
        compute='_compute_operadora',  # Añadir compute
        store=True)  # Añadir store=True

    plan_id = fields.Many2one('fundacupaz.phone.plan', string='Planes')
    ente = fields.Many2one('fundacupaz.ente', string="Ente Asignado", tracking=True)
    persona_asignada = fields.Many2one('res.partner', domain="[('is_company', '!=','true')]", string="Persona Asignada",
                                       tracking=True)
    estatus = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('ACTIVA', 'ACTIVA'),
            ('INACTIVA', 'INACTIVA'),
            ('SUSPENDIDA', 'SUSPENDIDA')
        ],
        string='Estatus', default=False, tracking=True)
    estado = fields.Many2one(
        'res.country.state',
        domain=[('country_id.name', '=', 'Venezuela')],
        string="Estado", tracking=True
    )
    municipio = fields.Many2one('res.country.state.municipality', domain="[('state_id','=', estado)]",
                                string="Municipio", tracking=True)
    cuadrantes = fields.Many2one('fundacupaz.cuadrante', string="Cuadrante", tracking=True)
    observaciones = fields.Char("Observaciones", tracking=True)
    facturado_por = fields.Selection(
        selection=[
            ('Fundacupaz', 'Fundacupaz'),
            ('MIJ', 'MPPIJP'),
            ('Otros', 'Otros')
        ],
        string='Facturado a:', tracking=True)
    revisado = fields.Boolean("Revisado", tracking=True)
    fecha_revision = fields.Date("Fecha de Revisión", tracking=True)
    fecha_revision_time = fields.Datetime("Fecha de Revisión hora", tracking=True)
    is_fecha_revision_invisible = fields.Boolean(
        compute='_compute_is_fecha_revision_invisible',
        store=False, tracking=True
    )
    es_cuadrante = fields.Boolean("Es un cuadrante?", tracking=True)
    is_cuadrante_fields_invisible = fields.Boolean(
        compute='_compute_is_cuadrante_fields_invisible',
        store=False
    )
    llamado = fields.Boolean("Llamado", tracking=True)

    telf_corresponde = fields.Selection(
        selection=[
            ('si', 'Sí'),
            ('no', 'No')
        ],
        string="¿Teléfono verificado corresponde?",
        tracking=True
    )
    motivo_seleccionado = fields.Selection(
        selection=[
            ('N/D', 'No Disponible'),
            ('F/L', 'Fuera de línea / Apagado'),
            ('N/A', 'No Asignado'),
            ('S/D', 'Dañado / Suspendido por operadora'),
            ('otros', 'Otros')
        ],
        string="Motivo",
        tracking=True
    )
    motivo_otros_observaciones = fields.Text("Otras observaciones", tracking=True)

    telf_verificado = fields.Selection(
        selection=[
            ('ver01', 'Corresponde a Cuadrante'),
            ('ver02', 'No corresponde a Cuadrante'),
            ('ver03', 'No contesta'),
            ('ver04', 'Fuera de Linea')
        ],
        string='Telefono Verificado', default=False, tracking=True)

    # --- CAMBIO 2: Añadir la función de cálculo ---
    @api.depends('number_phone')
    def _compute_operadora(self):
        """
        Calcula y asigna la operadora basándose en el prefijo del número de teléfono.
        Al tener 'store=True', el resultado se guarda en la base de datos.
        """
        prefix_map = {
            '0412': 'DIGITEL',
            '0422': 'DIGITEL',
            '0414': 'MOVISTAR',
            '0424': 'MOVISTAR',
            '0416': 'MOVILNET',
            '0426': 'MOVILNET',
        }
        for record in self:
            operadora_detectada = False
            if record.number_phone and len(record.number_phone) >= 4:
                prefix = record.number_phone[0:4]
                operadora_detectada = prefix_map.get(prefix, False)
            record.operadora = operadora_detectada

    # --- CAMBIO 3: Simplificar el @api.onchange ---
    @api.onchange('number_phone')
    def _onchange_number_phone(self):
        """
        Esta función ahora solo se encarga de la interactividad de la UI:
        1. Limpiar el plan si la operadora cambia.
        2. Actualizar el dominio del campo 'plan_id'.
        """
        # La operadora se recalcula por el método _compute_operadora.
        # Aquí solo reaccionamos a ese cambio para actualizar otros campos.

        # Limpiar el plan_id ya que la operadora va a cambiar.
        # Odoo es lo suficientemente inteligente para detectar el cambio en el campo calculado
        # y saber que debe limpiar los campos que dependen de él.
        # Se puede forzar una limpieza para mejor respuesta de la UI.
        original_operadora = self._origin.operadora

        prefix_map = {
            '0412': 'DIGITEL', '0422': 'DIGITEL',
            '0414': 'MOVISTAR', '0424': 'MOVISTAR',
            '0416': 'MOVILNET', '0426': 'MOVILNET',
        }
        new_operadora = False
        if self.number_phone and len(self.number_phone) >= 4:
            prefix = self.number_phone[0:4]
            new_operadora = prefix_map.get(prefix, False)

        if new_operadora != original_operadora:
            self.plan_id = False

        # Devuelve el dominio para el campo 'plan_id' para que el usuario
        # solo vea los planes de la operadora correcta.
        if new_operadora:
            return {'domain': {'plan_id': [('operadora', '=', new_operadora)]}}
        else:
            return {'domain': {'plan_id': [('id', '=', False)]}}

    # ... (el resto de tus funciones no necesitan cambios)

    @api.onchange('llamado')
    def _onchange_llamado(self):
        """Si 'Llamado' se desmarca, limpia todos los campos de verificación."""
        if not self.llamado:
            self.telf_corresponde = False
            self.motivo_seleccionado = False
            self.motivo_otros_observaciones = ''

    @api.onchange('telf_corresponde')
    def _onchange_telf_corresponde(self):
        """Si la respuesta no es 'no', limpia los campos de motivo."""
        if self.telf_corresponde != 'no':
            self.motivo_seleccionado = False
            self.motivo_otros_observaciones = ''

    @api.onchange('motivo_seleccionado')
    def _onchange_motivo_seleccionado(self):
        """Si el motivo seleccionado no es 'Otros', limpia el campo de observaciones."""
        if self.motivo_seleccionado != 'otros':
            self.motivo_otros_observaciones = ''

    @api.depends('revisado')
    def _compute_is_fecha_revision_invisible(self):
        for record in self:
            record.is_fecha_revision_invisible = not record.revisado

    @api.onchange('revisado')
    def _onchange_revisado(self):
        """Si 'Revisado' se desmarca, vaciar 'Fecha de Revisión'."""
        if not self.revisado:
            self.fecha_revision_time = False

    @api.depends('es_cuadrante')
    def _compute_is_cuadrante_fields_invisible(self):
        for record in self:
            record.is_cuadrante_fields_invisible = not record.es_cuadrante

    @api.onchange('es_cuadrante')
    def _onchange_es_cuadrante(self):
        """Si 'Es un cuadrante?' se desmarca, vaciar 'Estado', 'Municipio' y 'Cuadrante'."""
        if not self.es_cuadrante:
            self.estado = False
            self.municipio = False
            self.cuadrantes = False

    @api.constrains('number_phone')
    def _check_phone_number_validation(self):
        valid_prefixes = ('0412', '0414', '0416', '0424', '0426', '0422')
        for record in self:
            if record.number_phone:
                phone_number = record.number_phone
                if not phone_number.isdigit():
                    raise ValidationError("El 'Número Telefono' solo debe contener dígitos (sin espacios ni guiones).")
                if len(phone_number) != 11:
                    raise ValidationError("El 'Número Telefono' debe tener exactamente 11 dígitos.")
                if not phone_number.startswith(valid_prefixes):
                    raise ValidationError(
                        "El 'Número Telefono' debe comenzar con un prefijo válido (0412, 0414, 0416, 0424, 0426, o 0422).")

    @api.constrains('estado')
    def _check_estado_comisionado(self):
        for record in self:
            user_estado_id = self.env.user.estado_comisionado.id if self.env.user.estado_comisionado else False
            if user_estado_id:
                if record.estado.id != user_estado_id:
                    raise ValidationError(
                        "El estado seleccionado no coincide con el estado asignado al comisionado actual.")