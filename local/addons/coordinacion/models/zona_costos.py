from odoo import fields, models

class ZonaCostos(models.Model):
    _name = "hcd.zona_costos"
    _description = "Zona de Costos"
    name = fields.Char("Descripción", required=True)
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
