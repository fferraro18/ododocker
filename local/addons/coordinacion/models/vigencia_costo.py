from odoo import fields, models

class VigenciaCosto(models.Model):
    _name = "hcd.vigencia_costo"
    _description = "Vigencia de costos"
    name = fields.Char()
    fecha_inicio = fields.Date()
    costo = fields.Float("Costo")
    fecha_fin = fields.Date()
    product_id = fields.Many2one(
        'product.template', string='Product Template',
    )
