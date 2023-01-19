# EN DESUSO   estaba en Servicio , no se usa mas 
from odoo import fields, models

class Discapacidad(models.Model):
    _name = "hcd.discapacidad"
    _description = "Discapacidad"
    name = fields.Char("Descripción", required=True)
    prefijo = fields.Char("Prefijo")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
