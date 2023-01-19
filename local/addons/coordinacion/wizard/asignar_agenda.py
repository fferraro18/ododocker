# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class AsignarAgenda(models.TransientModel):
    _name = 'hcd.asignar.agenda'
    _description = "Asignar"

    prestador_id = fields.Many2one(
        'res.partner', 'Prestador/Efector',
        domain="['|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector'),('status', '=', 'activo')]",
        help='Prestador asignado'
    )


    def asignar_agenda(self):
        agendas = self.env['hcd.agenda'].browse(self._context.get('active_ids',[]))
        for agenda in agendas:
            _logger.info("entra en bucles AGENDAS:  .................")
            _logger.info(agenda)
            agenda.update({'estado': 'asignado','prestador_id': self.prestador_id})
            # dic = {
            #     'product_id' : producto.id,
            #     'fecha_inicio' : producto.fecha_vigencia_costo,
            #     'fecha_fin' : self.fecha_inicio,
            #     'costo' : producto.costo
            # }
            # nuevo_costo = float(producto.costo) * ((self.porcentaje/100) + 1)
            # producto.update({'costo': nuevo_costo})
            # producto.update({'fecha_vigencia_costo': self.fecha_inicio})
            # self.env['hcd.vigencia_costo'].create(dic)     
            
            # self.env['product.template'].browse(self._context.get('active_ids')).update({'list_price': nuevo_costo})
        return True

