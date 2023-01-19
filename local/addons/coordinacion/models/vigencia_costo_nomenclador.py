from odoo import fields, models

class VigenciaCostoNomenclador(models.Model):
    _name = "hcd.vigencia_costo_nomenclador"
    _description = "Vigencia de costos de nomencladores"
    name = fields.Char()
    fecha_inicio = fields.Date()
    costo = fields.Float("Costo")
    fecha_fin = fields.Date()
    nomenclador_id = fields.Many2one(
        'hcd.nomenclador_costo', string='Costo Nomenclador',
    )
