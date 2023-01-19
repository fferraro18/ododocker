from odoo import fields, models

class Vigencia(models.Model):
    _name = "hcd.vigencia"
    _description = "Vigencia"
    name = fields.Char()
    fecha_inicio = fields.Date()
    price = fields.Float("Precio")
    fecha_fin = fields.Date()
    product_id = fields.Many2one(
        'product.template', string='Product Template',
    )
