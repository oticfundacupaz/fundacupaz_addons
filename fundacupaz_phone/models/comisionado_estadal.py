from odoo import fields, models, api
from odoo.exceptions import AccessError
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    es_comisionado = fields.Boolean(
        string="Es Comisionado Estatal",
        compute="_compute_es_comisionado",
        store=True
    )
    estado_comisionado = fields.Many2one(
        'res.country.state',
        domain="[('country_id.name', '=', 'Venezuela')]",
        string="Estado"
    )

    @api.depends('groups_id')
    def _compute_es_comisionado(self):
        """Detectar si el usuario pertenece al grupo de comisionados"""
        comisionado_group = self.env.ref('fundacupaz_phone.group_comisionados_estatales')
        for user in self:
            user.es_comisionado = comisionado_group in user.groups_id

    @api.model
    def create(self, vals):
        """Restricción: sólo usuarios del grupo pueden definir el estado"""
        if 'estado_comisionado' in vals:
            current_user = self.env.user
            comisionado_group = self.env.ref('fundacupaz_phone.group_comisionados_estatales')
            if comisionado_group not in current_user.groups_id:
                raise AccessError("No tienes permiso para asignar un estado como comisionado.")
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        """Restricción: sólo usuarios del grupo pueden modificar el estado"""
        if 'estado_comisionado' in vals:
            current_user = self.env.user
            comisionado_group = self.env.ref('fundacupaz_phone.group_comisionados_estatales')
            if comisionado_group not in current_user.groups_id:
                raise AccessError("No tienes permiso para modificar el estado asignado.")
        return super(ResUsers, self).write(vals)

    @api.constrains('estado_comisionado')
    def _check_estado_comisionado(self):
        for record in self:
            if record.estado_comisionado:
                existing_user = self.search([
                    ('estado_comisionado', '=', record.estado_comisionado.id),
                    ('id', '!=', record.id)
                ])
                if existing_user:
                    raise ValidationError(
                        f"El estado {record.estado_comisionado.name} ya está asignado a otro usuario."
                    )
