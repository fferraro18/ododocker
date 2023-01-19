from odoo import api, fields, models

class Equipamiento(models.Model):
    _inherit = "product.template"
    hcd_categ_prod = fields.Char() # valores : servicio | equipamiento | material | laboratorio | modulado
    hcd_eq_type = fields.Selection([
        ('SER', 'SER'),
        ('EQUIP', 'EQUIP'),
        ('EQUIP_OXIG', 'EQUIP_OXIG'),
        ('EQUIP_ORTOP', 'EQUIP_ORTOP'),
        ('EQUIP_EQAS', 'EQUIP_EQAS'),
        ('EQUIP_ELMED', 'EQUIP_ELMED'),
        ],
        help="Tipo de equipamiento") 
 
