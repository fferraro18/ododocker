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

    fecha_hasta = fields.Date()

    def prorrogar_viatico(self):
        gastos = self.env['hr.expense'].browse(
            self._context.get('active_ids', []))
        for gasto in gastos:
            new_rec = gasto.copy(
                {'fecha_hasta': self.fecha_hasta, 'prorrogado': True})
            _logger.info(f'Copiando Gasto: {new_rec}')
            _logger.info(f'Context: {self.env.context}')
            # gasto.update({'name': gasto.name, 'fecha_hasta': self.fecha_hasta})
        return True
