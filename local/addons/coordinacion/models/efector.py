from odoo import api, fields, models

class Efector(models.Model):
    _inherit = 'res.partner'

    prestador_id = fields.Many2one(
        'res.partner', 'Prestador/Empresa relacionada', 
        domain="[('hcd_type', '=', 'prestador'),('es_grupo', '=',True)]",
        help='Grupo al que pertenece'
    )
    