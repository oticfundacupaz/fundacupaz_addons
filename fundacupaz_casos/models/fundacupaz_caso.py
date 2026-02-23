# -*- coding: utf-8 -*-
from odoo.modules.module import get_module_resource
import random
import io
import base64
import xlsxwriter
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

    resumen_html = fields.Html(
        string="Resumen de Líneas",
        compute="_compute_resumen_html",
        store=False
    )

    @api.onchange('tipo_operacion')
    def _onchange_tipo_operacion_clean(self):
        """ Limpia los campos que no corresponden a la operación seleccionada """
        if self.tipo_operacion != 'traslado':
            self.nuevo_responsable_id = False

        if self.tipo_operacion != 'remision':
            self.ente_a_remitir = False
            self.fecha_remision = False

        if self.tipo_operacion == 'cancelacion':
            self.motivo = False

    @api.depends('line_ids', 'line_ids.operadora', 'line_ids.estado_id')
    def _compute_resumen_html(self):
        for record in self:
            if not record.line_ids:
                record.resumen_html = "<p class='text-muted'>Sin líneas cargadas.</p>"
                continue

            data = {}
            total_lines = 0

            for linea in record.line_ids:
                estado = linea.estado_id.name if linea.estado_id else 'Sin Estado'
                operadora = linea.operadora or 'N/A'

                if estado not in data:
                    data[estado] = {}
                if operadora not in data[estado]:
                    data[estado][operadora] = 0

                data[estado][operadora] += 1
                total_lines += 1

            html = "<table class='table table-sm table-bordered' style='width:100%; font-size:12px;'>"
            html += "<thead class='table-light'><tr><th>Estado</th><th>Operadora</th><th>Cantidad</th></tr></thead><tbody>"

            for estado, ops in data.items():
                rowspan = len(ops)
                first = True
                for op, count in ops.items():
                    html += "<tr>"
                    if first:
                        html += f"<td rowspan='{rowspan}' style='vertical-align:middle; font-weight:bold;'>{estado}</td>"
                        first = False
                    html += f"<td>{op}</td><td class='text-end'>{count}</td></tr>"

            html += f"<tr class='table-info'><td colspan='2'><strong>TOTAL LÍNEAS</strong></td><td class='text-end'><strong>{total_lines}</strong></td></tr>"
            html += "</tbody></table>"
            record.resumen_html = html

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

    def action_generar_excel(self):
        self.ensure_one()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Lineas")

        img_fundacion = get_module_resource('fundacupaz_casos', 'static/src/img', 'logo_fundacion.png')
        img_ministerio = get_module_resource('fundacupaz_casos', 'static/src/img', 'logo_ministerio.png')

        style_title = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'font_name': 'Arial'
        })
        style_subtitle = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 10, 'font_name': 'Arial'
        })
        style_header_table = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#D3D3D3', 'text_wrap': True
        })
        style_cell = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10
        })
        style_cell_left = workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_size': 10
        })

        sheet.set_column('A:A', 5)  # N°
        sheet.set_column('B:B', 20)  # Celular
        sheet.set_column('C:C', 30)  # Plan
        sheet.set_column('D:D', 20)  # Facturado A
        sheet.set_column('E:E', 22)  # Nro Cuenta

        sheet.set_row(0, 50)

        if img_fundacion:
            sheet.insert_image('E1', img_fundacion, {'x_scale': 0.7, 'y_scale': 0.5, 'x_offset': 5, 'y_offset': 5})

        if img_ministerio:
            sheet.insert_image('B1', img_ministerio, {'x_scale': 0.7, 'y_scale': 0.7, 'x_offset': 5, 'y_offset': 5})

        sheet.merge_range('A2:E2', "REPÚBLICA BOLIVARIANA DE VENEZUELA", style_title)
        sheet.merge_range('A3:E3', "MINISTERIO DEL PODER POPULAR PARA LAS RELACIONES INTERIORES JUSTICIA Y PAZ",
                          style_subtitle)
        sheet.merge_range('A4:E4', "FUNDACION GRAN MISION CUADRANTES DE PAZ ( FUNDACUPAZ)", style_subtitle)

        operadoras = ", ".join(set([l.operadora for l in self.line_ids if l.operadora])) or "VARIAS"
        estados = ", ".join(set([l.estado_id.name for l in self.line_ids if l.estado_id])) or "NACIONAL"
        tipo_op = dict(self._fields['tipo_operacion'].selection).get(self.tipo_operacion, '').upper()

        texto_dinamico = f"LINEAS ({operadoras}): DEL ESTADO ({estados}) PARA ({tipo_op})"
        sheet.merge_range('A6:E6', texto_dinamico, style_title)

        headers = ["N°", "CELULAR NUMERO", "PLAN", "FACTURADO A", "NUMERO DE CUENTA"]
        for col_num, header in enumerate(headers):
            sheet.write(7, col_num, header, style_header_table)

        row = 8
        count = 1
        for linea in self.line_ids:
            sheet.write(row, 0, count, style_cell)
            sheet.write(row, 1, linea.phone_id.number_phone or '', style_cell)
            sheet.write(row, 2, linea.plan_id.name if linea.plan_id else '', style_cell_left)
            sheet.write(row, 3, "FUNDACUPAZ", style_cell)
            sheet.write(row, 4, linea.numero_cuenta or '', style_cell)
            row += 1
            count += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': f"Reporte_Lineas_{self.codigo_caso}.xlsx",
            'type': 'binary',
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


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

    _sql_constraints = [
        ('unique_phone_in_case',
         'unique(caso_id, phone_id)',
         '¡Advertencia! No puedes agregar el mismo número telefónico dos veces en este caso.')
    ]

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

    def unlink(self):
        casos_afectados = self.mapped('caso_id')

        for caso in casos_afectados:
            lineas_del_caso = self.filtered(lambda l: l.caso_id == caso)
            numeros = ", ".join(lineas_del_caso.mapped('phone_id.number_phone'))

            caso.message_post(
                body=f"🗑️ <b>Líneas eliminadas:</b> Se quitaron los siguientes números del caso: {numeros}",
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )

        return super(FundacupazCasoLine, self).unlink()


class FundacupazCasoTag(models.Model):
    _name = 'fundacupaz.caso.tag'
    _description = 'Etiqueta de Caso'
    name = fields.Char('Nombre de Etiqueta', required=True)
    color = fields.Integer(
        string='Color',
        default=lambda self: random.randint(1, 11)
    )