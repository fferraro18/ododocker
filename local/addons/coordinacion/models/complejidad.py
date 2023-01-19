# EN DESUSO   estaba en Servicio , no se usa mas 
from odoo import fields, models

class Complejidad(models.Model):
    _name = "hcd.complejidad"
    _description = "Complejidad"
    name = fields.Char("Descripción", required=True)
    prefijo = fields.Char("Prefijo")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
