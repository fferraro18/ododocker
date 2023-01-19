from odoo import api,fields, models

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    cantidad_aprobada = fields.Integer()
    prestador_id = fields.Many2one(
        'res.partner', 'Prestador',
        domain="[('hcd_type', '=', 'prestador')]"
    ) 

    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        domain="[('hcd_type', '=', 'paciente')]"
    )
    