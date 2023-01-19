from odoo.exceptions import ValidationError
from odoo import api, fields, models
import re

class CategoriaNomenclador(models.Model):
    _name = "hcd.categoria_nomenclador"
    _description = "Categoria Nomenclador"
    name = fields.Char("Categoria", required=True)
    description = fields.Char("Descripcion")
    active = fields.Boolean("Activo", default=True)
    # fecha_creacion = fields.Date()
    prefijo = fields.Char("Prefijo", required=True)

    titulo_defecto_id = fields.Many2one(
        'hcd.profesion', 'Titulo por defecto'
    )

    tipo = fields.Selection([
        ('E', 'Enfermero'),
        ('C', 'Cuidador'),
        ('K', 'Kinesio'),
        ('M', 'Médico'),
        ('F', 'Fono'),
    ])

    titulos_ids = fields.Many2many(
         comodel_name="hcd.profesion",  relation='categoria_nomenclador_profesion_rel',
         string="Lista de titulos",
     )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre ya existe!'),
        ('prefijo_uniq', 'unique (prefijo)', 'El prefijo ya existe!'),
    ]

    @api.constrains('prefijo')
    def check_name_prefijo(self):
        for rec in self:
            if not re.match("^[A-Z]+$", rec.prefijo):
                raise ValidationError('El prefijo debe contener exactamente 4 letras mayúsculas')
            if  (len(rec.prefijo) != 4):
                raise ValidationError('El prefijo debe contener 4 caracteres')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.prefijo:
                name = name + " - " + rec.prefijo
            result.append((rec.id, name))
        return result

