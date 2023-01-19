from odoo import fields, models

class ZonaCobertura(models.Model):
    _name = "hcd.zona_cobertura"
    _description = "Zona de cobertura"
    name = fields.Char(required=True)
    description = fields.Char("Descripción")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
    color = fields.Integer()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'La zona ya existe!'),
    ]

