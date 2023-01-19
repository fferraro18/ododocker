# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ActualizoCostos(models.TransientModel):
    _name = 'hcd.actualizo.costos'
    _description = "Actualizo costos"

    porcentaje = fields.Float(string="porcentaje")
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

    def actualizar_costos(self):
        product_template = self.env['product.template'].browse(self._context.get('active_ids',[]))
        for producto in product_template:
     
            dic = {
                'product_id' : producto.id,
                'fecha_inicio' : producto.fecha_vigencia_costo,
                'fecha_fin' : self.fecha_inicio,
                'costo' : producto.costo
            }
            nuevo_costo = float(producto.costo) * ((self.porcentaje/100) + 1)
            producto.update({'costo': nuevo_costo})
            producto.update({'fecha_vigencia_costo': self.fecha_inicio})
            self.env['hcd.vigencia_costo'].create(dic)     
            
            # self.env['product.template'].browse(self._context.get('active_ids')).update({'list_price': nuevo_costo})
        return True

