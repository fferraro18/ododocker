from odoo import fields, models

class ZonaGeografica(models.Model):
    _name = "hcd.zona_geografica"
    _description = "Zona Geografica"
    name = fields.Char("Descripción", required=True)
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
