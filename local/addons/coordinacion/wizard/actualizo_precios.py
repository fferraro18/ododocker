# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ActualizoPrecios(models.TransientModel):
    _name = 'hcd.actualizo.precios'
    _description = "Actualizo precios"

    porcentaje = fields.Float(string="Porcentaje")
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()

    @api.constrains('fecha_inicio','fecha_fin')
    def _check_two_date_comp(self):
        for record in self:
                if (record.fecha_fin):
                    start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                    end_date = record.fecha_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
                        
    def actualizar_precios(self):
        product_template = self.env['product.template'].browse(self._context.get('active_ids',[]))
        for producto in product_template:
            dic = {
                'product_id' : producto.id,
                'fecha_inicio' : producto.fecha_inicio,
                'fecha_fin' : self.fecha_inicio,
                'price' : producto.list_price
            }

            nuevo_precio = float(producto.list_price) * ((self.porcentaje/100) + 1)
            producto.update({'list_price': nuevo_precio})
            producto.update({'fecha_inicio': self.fecha_inicio,})
            self.env['hcd.vigencia'].create(dic)
            # self.env['product.template'].browse(self._context.get('active_ids')).update({'list_price': nuevo_precio})
        return True