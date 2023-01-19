from odoo import fields, models

class Feriados(models.Model):
    _name = "hcd.feriados"
    _description = "Feriados"
    name = fields.Char("Descripción",required=True)
    feriado = fields.Date(required=True)
    active = fields.Boolean("Activo?", default=True)
    
    _sql_constraints = [
        ('feriado_uniq', 'unique (feriado)', 'La fecha ya fue agregada'),
    ]
