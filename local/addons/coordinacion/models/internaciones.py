from odoo import fields, models

class Internaciones(models.Model):
    _name = "hcd.internaciones"
    _description = "Internaciones"
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()
    diagnostico_id = fields.Many2one(
        comodel_name='hcd.diagnostico', string='Diagnóstico',
        help='Diagnóstico internación'
    )
    paciente_id = fields.Many2one(
        'res.partner', string='Paciente',
    )
    observaciones = fields.Char()
    
