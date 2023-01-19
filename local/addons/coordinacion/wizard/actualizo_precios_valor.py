# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ActualizoPreciosValor(models.TransientModel):
    _name = 'hcd.actualizo.precios.valor'
    _description = "Actualizo precios por valor"

    precio = fields.Float(string="Precio")
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()

    @api.constrains('precio')
    def _check_something(self):
        for record in self:
            if record.precio < 0:
                raise ValidationError('El precio debe ser positivo!')


    @api.constrains('fecha_inicio','fecha_fin')
    def _check_two_date_comp(self):
        for record in self:
                if (record.fecha_fin):
                    start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                    end_date = record.fecha_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    def actualizar_precios_valor(self):
        product_template = self.env['product.template'].browse(self._context.get('active_ids',[]))
        for producto in product_template:
            dic = {
                'product_id' : producto.id,
                'fecha_inicio' : producto.fecha_inicio,
                'fecha_fin' : self.fecha_inicio,
                'price' : producto.list_price
            }

            producto.update({'list_price': self.precio})
            producto.update({'fecha_inicio': self.fecha_inicio})
            self.env['hcd.vigencia'].create(dic)
            # self.env['product.template'].browse(self._context.get('active_ids')).update({'list_price': nuevo_precio})
        return True
