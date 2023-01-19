from odoo import fields, models


class DiasSemana(models.TransientModel):
    _name = "hcd.dia.semana"
    _description = "Dias de la semana"
    id = fields.Integer()
    name = fields.Char("Dia", required=True)
    abreviado = fields.Char("Abreviatura", required=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.abreviado))
        return result