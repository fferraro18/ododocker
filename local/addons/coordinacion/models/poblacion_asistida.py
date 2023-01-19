from odoo import fields, models
import re

class PoblacionAsistida(models.Model):
    _name = "hcd.poblacion_asistida"
    _description = "Población Asistida"
    name = fields.Char(required=True)
    description = fields.Char("Descripcion")
    active = fields.Boolean("Activo", default=True)
    color = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre ya existe!'),
    ]

