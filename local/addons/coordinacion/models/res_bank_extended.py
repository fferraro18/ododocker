from odoo.exceptions import ValidationError
from odoo import api,fields, models
import re

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    cbu = fields.Char('CBU')  
    alias = fields.Char() 
    titular = fields.Char('Titular')
    cuit = fields.Integer('CUIT') 
    tipo_cuenta = fields.Selection([
        ('1','Caja de ahorro ARS'),
        ('2','Cuenta corriente ARS'),
        ('3','Caja de ahorro USD'),
        ('4','Cuenta corriente USD'),],string="Tipo de Cta")

    @api.constrains('cbu')
    def check_cbu(self):
        for rec in self:
            if not re.match("^[0-9]+$", rec.cbu):
                raise ValidationError('El CBU debe contener 22 nros')
            if  (len(rec.cbu) != 22):
                raise ValidationError('El CBU debe contener 22 nros')
