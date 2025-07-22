# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.exceptions import ValidationError


class FundacupazPhone(models.Model):
    _name = "fundacupaz.phone"
    _inherit = "mail.thread"

    number_phone = fields.Char("Número Telefono", tracking=True)
    marca_phone = fields.Char("Marca", tracking=True)
    modelo_phone = fields.Char("Modelo", tracking=True)
    imei_phone = fields.Char("IMEI", tracking=True)
    operadora = fields.Selection(
        selection=[
            ('MOVILNET', 'MOVILNET'),
            ('MOVISTAR', 'MOVISTAR'),
            ('DIGITEL', 'DIGITEL')
        ],
    string='Operadora', tracking=True)
    planes = fields.Selection(
        selection=[
            ('N/A', 'N/A'),
            ('MOVILNET EMPRENDE 10', 'MOVILNET EMPRENDE 10'),
            ('MOVISTAR PLUS 25 GB', 'MOVISTAR PLUS 25 GB'),
            ('MOVISTAR PLUS 10 GB', 'MOVISTAR PLUS 10 GB'),
            ('DIGITEL INTELIGENTE PLUS 1.1GB', 'DIGITEL INTELIGENTE PLUS 1.1GB'),
            ('DIGITEL INTELIGENTE PLUS 2GB', 'DIGITEL INTELIGENTE PLUS 2GB'),
            ('DIGITEL INTELIGENTE PLUS 6GB', 'DIGITEL INTELIGENTE PLUS 6GB'),
            ('DIGITEL INTELIGENTE PLUS 30GB', 'DIGITEL INTELIGENTE PLUS 30GB')
        ],
        string='Planes', tracking=True)
    ente = fields.Many2one('fundacupaz.ente',string="Ente Asignado", tracking=True)
    persona_asignada = fields.Many2one('res.partner',domain="[('is_company', '!=','true')]",string="Persona Asignada", tracking=True )
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
        domain=[('country_id.name','=','Venezuela')],
        string="Estado", tracking=True
    )
    municipio = fields.Many2one('res.country.state.municipality' ,domain="[('state_id','=', estado)]", string="Municipio", tracking=True)
    cuadrantes = fields.Many2one('fundacupaz.cuadrante' , string="Cuadrante", tracking=True)
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

    # --- INICIO DE CAMBIOS REQUERIDOS ---
    # Se elimina el campo 'telf_verificado' y se agregan los nuevos campos.
    telf_corresponde = fields.Selection(
        selection=[
            ('si', 'Sí'),
            ('no', 'No')
        ],
        string="¿Teléfono verificado corresponde?",
        tracking=True
    )
    # MODIFICACIÓN: Campo de selección para los motivos
    motivo_seleccionado = fields.Selection( #
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

    @api.onchange('llamado')
    def _onchange_llamado(self):
        """Si 'Llamado' se desmarca, limpia todos los campos de verificación."""
        if not self.llamado:
            self.telf_corresponde = False
            self.motivo_seleccionado = False # CAMBIO AQUÍ
            self.motivo_otros_observaciones = ''

    @api.onchange('telf_corresponde')
    def _onchange_telf_corresponde(self):
        """Si la respuesta no es 'no', limpia los campos de motivo."""
        if self.telf_corresponde != 'no':
            self.motivo_seleccionado = False # CAMBIO AQUÍ
            self.motivo_otros_observaciones = '' # Asegurarse de limpiar también las observaciones

    @api.onchange('motivo_seleccionado') # NUEVO MÉTODO ONCHANGE
    def _onchange_motivo_seleccionado(self):
        """Si el motivo seleccionado no es 'Otros', limpia el campo de observaciones."""
        if self.motivo_seleccionado != 'otros':
            self.motivo_otros_observaciones = ''
    # --- FIN DE CAMBIOS REQUERIDOS ---


    @api.depends('revisado')
    def _compute_is_fecha_revision_invisible(self):
        for record in self:
            record.is_fecha_revision_invisible = not record.revisado

    @api.onchange('revisado')
    def _onchange_revisado(self):
        """Si 'Revisado' se desmarca, vaciar 'Fecha de Revisión'."""
        if not self.revisado:
            self.fecha_revision = False

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

    @api.constrains('estado')
    def _check_estado_comisionado(self):
        for record in self:
            user_estado_id = self.env.user.estado_comisionado.id if self.env.user.estado_compositionado else False
            if user_estado_id:
                if record.estado.id != user_estado_id:
                    raise ValidationError("El estado seleccionado no coincide con el estado asignado al comisionado actual.")