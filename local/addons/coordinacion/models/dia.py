# EN DESUSO   estaba en Servicio , no se usa mas 
from odoo import fields, models

class Dia(models.Model):
    _name = "hcd.dia"
    _description = "SADOFE"
    name = fields.Char("Descripción", required=True)
    prefijo = fields.Char("Prefijo")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()
