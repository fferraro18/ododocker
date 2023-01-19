from odoo import fields, models

class Nodo(models.Model):
    _name = "hcd.nodo"
    _description = "Nodo"
    name = fields.Char(required=True)
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El Nodo ya existe!'),
        ]
