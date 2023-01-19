# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models, _
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class LiquidoPrestador(models.TransientModel):
    _name = 'hcd.liquido.prestador'
    _description = "Liq. Prestadores - Búsqueda"

    prestador_id = fields.Many2one(
        'res.partner', 'Prestador',
        domain="[('hcd_type', '=', 'prestador')]"
    )
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()


    @api.constrains('fecha_inicio','fecha_fin')
    def _check_two_date_comp_lp(self):
        for record in self:
                if (record.fecha_fin):
                    start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                    end_date = record.fecha_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    def busco_prestador(self):
        for applicant in self:
            prestador_id = applicant.prestador_id.id
            fecha_inicio = applicant.fecha_inicio
            fecha_fin = applicant.fecha_fin
            return {
            'name': _('Prestaciones'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model':'hcd.agenda',
                'domain': [('prestador_id', '=' , prestador_id),('estado', '=' , 'ejecutado'),('fecha_visita', '>=', fecha_inicio),('fecha_visita', '<=', fecha_fin)]
        }


 
