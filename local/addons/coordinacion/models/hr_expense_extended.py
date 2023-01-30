from markupsafe import string
from traitlets import default
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    cantidad_aprobada = fields.Integer()
    fecha_hasta = fields.Date()
    prorrogado = fields.Boolean(default=False)

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
