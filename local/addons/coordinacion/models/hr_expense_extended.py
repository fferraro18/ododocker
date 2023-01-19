from odoo import api,fields, models

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    cantidad_aprobada = fields.Integer()
    fecha_hasta = fields.Date()
    prestador_id = fields.Many2one(
        'res.partner', 'Prestador',
        domain="['|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector')]"
    ) 

    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        domain="[('hcd_type', '=', 'paciente')]"
    )

    plan_trabajo_line_id = fields.Many2one(
        'hcd.plan_trabajo_line', 'Prestación del plan de trabajo'
    )