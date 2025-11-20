# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FundacupazPhone(models.Model):
    _name = "fundacupaz.phone"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Registro de Teléfonos'

    # Campos de información básica
    number_phone = fields.Char("Número Telefono", tracking=True, size=11)
    marca_phone = fields.Char("Marca", tracking=True)
    modelo_phone = fields.Char("Modelo", tracking=True)
    imei_phone = fields.Char("IMEI", tracking=True)
    observaciones = fields.Char("Si es otro:", tracking=True)
    observaciones_llamada = fields.Text("Observaciones de Llamada Efectiva", tracking=True)

    # Campos de estado y clasificación
    operadora = fields.Selection(
        selection=[
            ('MOVILNET', 'MOVILNET'),
            ('MOVISTAR', 'MOVISTAR'),
            ('DIGITEL', 'DIGITEL')
        ],
        string='Operadora',
        tracking=True,
        compute='_compute_operadora',
        store=True
    )
    estatus = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('ACTIVA', 'ACTIVA'),
            ('INACTIVA', 'INACTIVA'),
            ('SUSPENDIDA', 'SUSPENDIDA'),
            ('CANCELADO', 'CANCELADO')
        ],
        string='Estatus', default=False, tracking=True
    )
    facturado_por = fields.Selection(
        selection=[
            ('Fundacupaz', 'Fundacupaz'),
            ('MIJ', 'MPPIJP'),
            ('Otros', 'Otros')
        ],
        string='Facturado a:', tracking=True
    )

    numero_cuenta = fields.Char("Número de Cuenta", tracking=True)
    revisado = fields.Boolean("Revisado", tracking=True)
    llamado = fields.Boolean("Llamado", tracking=True)
    es_cuadrante = fields.Boolean("Es un cuadrante?", tracking=True)

    planes = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('MOVILNET EMPRENDE 10', 'MOVILNET EMPRENDE 10'),
            ('MOVISTAR PLUS 25 GB', 'MOVISTAR PLUS 25 GB'),
            ('MOVISTAR PLUS 10 GB', 'MOVISTAR PLUS 10 GB'),
            ('DIGITEL INTELIGENTE PLUS 1.1GB', 'DIGITEL INTELIGENTE PLUS 1.1GB'),
            ('DIGITEL INTELIGENTE PLUS 2GB', 'DIGITEL INTELIGENTE PLUS 2GB'),
            ('DIGITEL INTELIGENTE PLUS 6GB', 'DIGITEL INTELIGENTE PLUS 6GB'),
            ('DIGITEL INTELIGENTE PLUS 30GB', 'DIGITEL INTELIGENTE PLUS 30GB'),
            ('INTERNET MOVIL 1GB', 'INTERNET MOVIL 1GB'),
            ('RADI-CALL PLUS 4G LTE', 'RADI-CALL PLUS 4G LTE')
        ],
        string='Planes', tracking=True)
    # Campos de relación
    plan_id = fields.Many2one('fundacupaz.phone.plan', string='Planes', tracking=True)
    ente = fields.Many2one('fundacupaz.ente', string="Ente Asignado", tracking=True)
    persona_asignada = fields.Many2one('res.partner', domain="[('is_company', '!=','true')]", string="Responsable", tracking=True)
    estado = fields.Many2one('res.country.state', domain=[('country_id.name', '=', 'Venezuela')], string="Estado", tracking=True)
    municipio = fields.Many2one('res.country.state.municipality', domain="[('state_id','=', estado)]", string="Municipio", tracking=True)
    cuadrantes = fields.Many2one('fundacupaz.cuadrante', string="Cuadrante", tracking=True)

    # Campos de revisión y verificación
    fecha_revision = fields.Date("Fecha de Revisión", tracking=True)
    fecha_revision_time = fields.Datetime("Fecha de Revisión hora", tracking=True)
    operador_id = fields.Many2one(
        'res.users',
        string='Operador',
        tracking=True,
        readonly=True,
        help="Usuario que realizó la última verificación.")
    is_fecha_revision_invisible = fields.Boolean(store=False, tracking=True)
    is_cuadrante_fields_invisible = fields.Boolean(compute='_compute_is_cuadrante_fields_invisible', store=False)
    telf_corresponde = fields.Selection(
        selection=[
            ('si', 'Sí'),
            ('no', 'No')
        ],
        string="¿La llamada fue efectiva?", tracking=True)

    parroqui_comuna = fields.Char("Parroquia", tracking=True)
    circuito_comuna = fields.Char("circuito comunal", tracking=True)

    motivo_seleccionado = fields.Selection(
        selection=[
            ('N/D', 'Repica y no responde'),
            ('F/L', 'Fuera de cobertura / Apagado'),
            ('N/A', 'No Asignado'),
            ('S/D', 'Suspendido temporalmente')
        ],
        string="Motivo", tracking=True)

    motivo_otros_observaciones = fields.Text("Observaciones de llamada no efectiva", tracking=True)
    telf_verificado = fields.Selection(
        selection=[
            ('ver01', 'Corresponde a Cuadrante'),
            ('ver02', 'No corresponde a Cuadrante'),
            ('ver03', 'No contesta'),
            ('ver04', 'Fuera de Linea')
        ],
        string='Telefono Verificado', default=False, tracking=True)

    organismo = fields.Selection(
        selection=[
            ('P/E', 'POLICIA DEL ESTADO'),
            ('P/M', 'POLICIA MUNICIPAL'),
            ('GNB', 'GNB'),
            ('CPNB', 'CPNB'),
            ('OTRO', 'OTRO')
        ],
        string="Organismo", tracking=True)

    organismo_otro = fields.Char(
        string="Especifique el Organismo",
        tracking=True
    )

    is_editor_basico = fields.Boolean(
        string="Es Editor Básico",
        compute='_compute_is_editor_basico'
    )

    Moto = fields.Selection(
        selection=[
            ('si', 'Sí'),
            ('no', 'No')
        ],
        string="¿Usa Moto?",
        default='no',
        tracking=True
    )
    marca_Moto_id = fields.Many2one(
        'fundacupaz.moto.marca',
        string="Marca de la Moto",
        tracking=True
    )
    modelo_Moto_id = fields.Many2one(
        'fundacupaz.moto.modelo',
        string="Modelo de la Moto",
        tracking=True
    )
    serial_Moto = fields.Char(
        string="Serial de la Moto",
        tracking=True
    )

    def write(self, vals):
        """
        Sobreescribe write para actualizar la fecha y el operador de revisión
        únicamente cuando se modifica el campo 'telf_corresponde'.
        """
        # Verifica si 'telf_corresponde' es una de las claves que se está actualizando.
        if 'telf_corresponde' in vals:
            if self.env.user and self.env.user.id != self.env.ref('base.user_root').id:
                # Si se está estableciendo un valor en telf_corresponde, actualiza fecha y operador.
                if vals.get('telf_corresponde'):
                    vals['fecha_revision_time'] = fields.Datetime.now()
                    vals['operador_id'] = self.env.user.id
                # Si se está limpiando telf_corresponde, limpia también fecha y operador.
                else:
                    vals['fecha_revision_time'] = False
                    vals['operador_id'] = False

        return super(FundacupazPhone, self).write(vals)

    @api.depends_context('uid')
    def _compute_is_editor_basico(self):
        """Calcula si el usuario actual pertenece al grupo 'Editor Básico'."""
        self.is_editor_basico = self.env.user.has_group('fundacupaz_phone.grupo_fundacupaz_editor_basico')

    # Métodos Compute
    @api.depends('number_phone')
    def _compute_operadora(self):
        """
        Calcula y asigna la operadora basándose en el prefijo del número de teléfono.
        Al tener 'store=True', el resultado se guarda en la base de datos.
        """
        prefix_map = {
            '0412': 'DIGITEL', '0422': 'DIGITEL',
            '0414': 'MOVISTAR', '0424': 'MOVISTAR',
            '0416': 'MOVILNET', '0426': 'MOVILNET',
        }
        for record in self:
            operadora_detectada = False
            if record.number_phone and len(record.number_phone) >= 4:
                prefix = record.number_phone[0:4]
                operadora_detectada = prefix_map.get(prefix, False)
            record.operadora = operadora_detectada



    @api.depends('es_cuadrante')
    def _compute_is_cuadrante_fields_invisible(self):
        for record in self:
            record.is_cuadrante_fields_invisible = not record.es_cuadrante

    # Métodos Onchange
    @api.onchange('organismo')
    def _onchange_organismo(self):
        """Limpia el campo de especificación si la opción seleccionada no es 'OTRO'."""
        if self.organismo != 'OTRO':
            self.organismo_otro = False

    @api.onchange('Moto')
    def _onchange_Moto(self):
        """Limpia los campos de moto si '¿Usa Moto?' se marca como 'No'."""
        if self.Moto == 'no':
            # CORREGIDO: Usamos los nuevos nombres de los campos
            self.marca_Moto_id = False  # Antes decía: self.marca_Moto
            self.modelo_Moto_id = False  # Nuevo campo
            self.serial_Moto = False  # Este se mantiene igual si no lo cambiaste

    # Asegúrate de tener también este método para filtrar los modelos:
    @api.onchange('marca_Moto_id')
    def _onchange_marca_Moto_id(self):
        """Limpia el Modelo si la Marca ha cambiado y filtra la lista."""
        self.modelo_Moto_id = False  # Limpia el modelo anterior
        if self.marca_Moto_id:
            # Filtra los modelos que pertenecen a la marca seleccionada
            return {'domain': {'modelo_Moto_id': [('marca_id', '=', self.marca_Moto_id.id)]}}
        else:
            return {'domain': {'modelo_Moto_id': [('id', '=', False)]}}

    @api.onchange('number_phone')
    def _onchange_number_phone(self):
        """
        Actualiza el dominio del campo 'plan_id' y limpia el plan si la operadora cambia.
        """
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

        if new_operadora:
            return {'domain': {'plan_id': [('operadora', '=', new_operadora)]}}
        else:
            return {'domain': {'plan_id': [('id', '=', False)]}}

    @api.onchange('telf_corresponde')
    def _onchange_telf_corresponde(self):
        """
        Establece la fecha/hora/operador y limpia los campos de motivo/observación
        según si la llamada fue efectiva o no.
        """
        if self.telf_corresponde:
            self.fecha_revision_time = fields.Datetime.now()
            self.operador_id = self.env.user.id
        else:
            self.fecha_revision_time = False
            self.operador_id = False

        if self.telf_corresponde == 'si':
            # Si la llamada es efectiva, limpiar los campos del caso 'no'
            self.motivo_seleccionado = False
            self.motivo_otros_observaciones = ''
        elif self.telf_corresponde == 'no':
            # Si la llamada no es efectiva, limpiar los campos del caso 'si'
            self.observaciones_llamada = ''


    @api.onchange('es_cuadrante')
    def _onchange_es_cuadrante(self):
        """Si 'Es un cuadrante?' se desmarca, vaciar 'Estado', 'Municipio' y 'Cuadrante'."""
        if not self.es_cuadrante:
            self.estado = False
            self.municipio = False
            self.cuadrantes = False

    # Métodos Constrain
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