from odoo import fields, models

class Convenio(models.Model):
    _name = "hcd.convenio"
    _description = "Convenios"
    name = fields.Char("Nombre del convenio", required=True)
    descripcion = fields.Char("Descripción")
    prefijo = fields.Char("Prefijo")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
