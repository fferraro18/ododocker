# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ProrrogarViatico(models.TransientModel):
    _name = 'hr.prorrogar.viatico'
    _description = "Prorroga de Viaticos"

    fecha_hasta= fields.Date()
    prestador_id = fields.Many2one(
        'res.partner', 'Prestador/Efector',
        domain="['|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector'),('status', '=', 'activo')]",
        help='Prestador asignado'
    )

    def prorrogar_viatico(self):
        print("Prorroga....")
        print(self)
        gastos = self.env['hr.expense'].browse(self._context.get('active_ids',[]))
        for gasto in gastos:
             _logger.info("entra en bucles GASTOS:  .................")
             _logger.info(gasto)
             gasto.update({'name': gasto.name ,'fecha_hasta': self.fecha_hasta})
        return True
