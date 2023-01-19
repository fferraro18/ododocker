from odoo import fields, models

class Diagnostico(models.Model):
    _name = "hcd.diagnostico"
    _description = "Clasificación internacional de enfermedades CIE10"
    name = fields.Char("Código", required=True)
    descripcion = fields.Char("Descripción", required=True)
    

    def name_get(self):
        res = []
        for activista in self:
            name = f'[{activista.name}] {activista.descripcion}'
            res.append((activista.id, name))
        return res