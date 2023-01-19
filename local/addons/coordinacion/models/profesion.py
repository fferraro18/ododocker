from odoo import fields, models

class Profesion(models.Model):
    _name = "hcd.profesion"
    _description = "Profesiones"
    name = fields.Char("Descripción", required=True)
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
