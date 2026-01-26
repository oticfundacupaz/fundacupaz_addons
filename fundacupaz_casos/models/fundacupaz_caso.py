# -*- coding: utf-8 -*-
import random
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FundacupazCaso(models.Model):
    _name = "fundacupaz.caso"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Gestión de Casos (Lotes)'
    _rec_name = 'codigo_caso'

    codigo_caso = fields.Char(
        string="Código",
        required=True, copy=False, readonly=True,
        default=lambda self: _('Nuevo')
    )
    tag_ids = fields.Many2many(
        'fundacupaz.caso.tag',
        string="Etiquetas",
        help="Etiquetas para clasificar y buscar casos fácilmente."
    )

    tipo_operacion = fields.Selection([
        ('traslado', 'Traslado de Responsable'),
        ('remision', 'Remisión a Ente'),
        ('cancelacion', 'Cancelación de Línea')
    ], string="Tipo de Operación", required=True, default='traslado', tracking=True)

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('solicitado', 'Solicitado'),
        ('aprobado', 'Aprobado/Procesado'),
        ('cancelado', 'Anulado'),
    ], string='Estado', default='borrador', tracking=True)


    remision_finalizada = fields.Boolean(
        string="Remisión Finalizada",
        default=False,
        copy=False,
        tracking=True,
        help="Indica si los teléfonos ya fueron retornados a su estatus original."
    )

    fecha_solicitud = fields.Date(string="Fecha Solicitud", default=fields.Date.today, required=True)


    nuevo_responsable_id = fields.Many2one(
        'res.partner',
        string="Nuevo Responsable",
        domain="[('is_company', '!=', True)]",
        tracking=True
    )


    ente_a_remitir = fields.Selection([
        ('MOVISTAR', 'MOVISTAR'),
        ('DIGITEL', 'DIGITEL'),
        ('MOVILNET', 'MOVILNET'),
        ('MIJP', 'MIJP'),
        ('VEN911', 'VEN911')
    ], string="Ente a Remitir", tracking=True)

    fecha_remision = fields.Date(string="Fecha de Remisión", tracking=True)


    motivo = fields.Selection([
        ('asignacion', 'Asignación Inicial'),
        ('cambio_cargo', 'Cambio de Cargo'),
        ('robo', 'Robo / Extravío'),
        ('deterioro', 'Deterioro / Daño'),
        ('no_requerido', 'Ya no se requiere'),
        ('administrativo', 'Decisión Administrativa'),
        ('otro', 'Otro')
    ], string="Motivo", required=True, tracking=True)

    descripcion = fields.Text("Observaciones Generales")

    line_ids = fields.One2many(
        'fundacupaz.caso.line',
        'caso_id',
        string="Teléfonos a Procesar"
    )

    @api.model
    def create(self, vals):
        if vals.get('codigo_caso', _('Nuevo')) == _('Nuevo'):
            vals['codigo_caso'] = self.env['ir.sequence'].next_by_code('fundacupaz.caso') or _('Nuevo')
        return super(FundacupazCaso, self).create(vals)

    def action_solicitar(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError("Debe agregar al menos una línea telefónica para procesar.")

        if self.tipo_operacion == 'traslado' and not self.nuevo_responsable_id:
            raise ValidationError("Para un Traslado, debe indicar el Nuevo Responsable.")

        if self.tipo_operacion == 'remision' and (not self.ente_a_remitir or not self.fecha_remision):
            raise ValidationError("Para una Remisión, debe indicar el Ente y la Fecha de Remisión.")

        self.state = 'solicitado'

    def action_aprobar(self):
        """ Aplica los cambios a todos los teléfonos de la lista """
        self.ensure_one()

        for linea in self.line_ids:
            telefono = linea.phone_id

            if self.tipo_operacion == 'traslado':

                telefono.write({
                    'persona_asignada': self.nuevo_responsable_id.id,
                    'ente': self.nuevo_responsable_id.ente_id.id if hasattr(self.nuevo_responsable_id,
                                                                            'ente_id') else telefono.ente.id
                })
                telefono.message_post(
                    body=f"🔄 TRASLADO (Caso {self.codigo_caso}): Asignado a {self.nuevo_responsable_id.name}.")

            elif self.tipo_operacion == 'remision':

                estatus_actual = telefono.estatus or 'N/A'

                telefono.write({
                    'estatus_previo': estatus_actual,
                    'estatus': 'INACTIVA',
                    'observaciones': f"Remitido a {self.ente_a_remitir} el {self.fecha_remision} (Caso {self.codigo_caso})"
                })

                telefono.message_post(
                    body=f"🏢 REMISIÓN (Caso {self.codigo_caso}): Remitido a {self.ente_a_remitir}. Estatus temporal: INACTIVA.")

            elif self.tipo_operacion == 'cancelacion':
                telefono.write({'estatus': 'CANCELADO', 'estatus_previo': False})
                telefono.message_post(
                    body=f"⛔ CANCELACIÓN (Caso {self.codigo_caso}): Motivo: {dict(self._fields['motivo'].selection).get(self.motivo)}.")

        self.state = 'aprobado'

    def action_finalizar_remision(self):
        """ Restaura el estatus original y oculta el botón """
        self.ensure_one()
        if self.tipo_operacion != 'remision':
            return

        for linea in self.line_ids:
            telefono = linea.phone_id
            if telefono.estatus_previo:
                telefono.write({
                    'estatus': telefono.estatus_previo,
                    'estatus_previo': False,
                    'observaciones': f"{telefono.observaciones or ''} | Retornado de remisión {self.fecha_remision}."
                })
                telefono.message_post(
                    body=f"✅ FIN DE REMISIÓN (Caso {self.codigo_caso}): Estatus restaurado a {telefono.estatus}.")

        self.remision_finalizada = True
        self.message_post(body="El proceso de remisión ha sido finalizado y los teléfonos restaurados.")

    def action_cancelar_caso(self):
        self.state = 'cancelado'

    def action_borrador(self):
        self.state = 'borrador'


class FundacupazCasoLine(models.Model):
    _name = 'fundacupaz.caso.line'
    _description = 'Línea de Caso Telefónico'

    caso_id = fields.Many2one('fundacupaz.caso', string="Caso Padre", ondelete='cascade')

    phone_id = fields.Many2one(
        'fundacupaz.phone',
        string="Número de Teléfono",
        required=True,
        domain="[('estatus', '!=', 'CANCELADO')]"
    )

    operadora = fields.Selection(
        related='phone_id.operadora',
        string="Operadora",
        readonly=True,
        store=True
    )
    plan_id = fields.Many2one(
        related='phone_id.plan_id',
        string="Plan",
        readonly=True
    )

    persona_asignada = fields.Many2one(
        related='phone_id.persona_asignada',
        string="Responsable Actual",
        readonly=True
    )
    numero_cuenta = fields.Char(
        related='phone_id.numero_cuenta',
        string="Nro. Cuenta",
        readonly=True
    )
    estatus_phone = fields.Selection(
        related='phone_id.estatus',
        string="Estatus Actual",
        readonly=True
    )
    estado_id = fields.Many2one(
        related='phone_id.estado',
        string="Estado (Región)",
        readonly=True
    )

    @api.onchange('phone_id')
    def _onchange_phone_id_check_pending(self):
        if self.phone_id:
            casos_pendientes = self.env['fundacupaz.caso.line'].search([
                ('phone_id', '=', self.phone_id.id),
                ('caso_id.state', '=', 'solicitado'),
                ('id', '!=', self._origin.id)
            ])

            if casos_pendientes:
                codigo_otro = casos_pendientes[0].caso_id.codigo_caso
                self.phone_id = False
                return {
                    'warning': {
                        'title': _("⚠️ Teléfono en Trámite"),
                        'message': _("El número seleccionado ya está en proceso en el caso %s.") % codigo_otro
                    }
                }


class FundacupazCasoTag(models.Model):
    _name = 'fundacupaz.caso.tag'
    _description = 'Etiqueta de Caso'
    name = fields.Char('Nombre de Etiqueta', required=True)
    color = fields.Integer(
        string='Color',
        default=lambda self: random.randint(1, 11)
    )