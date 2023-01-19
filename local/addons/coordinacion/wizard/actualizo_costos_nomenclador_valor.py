# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ActualizoCostosValor(models.TransientModel):
    _name = 'hcd.actualizo.costos.nomenclador.valor'
    _description = "Actualizo costos por valor"

    costo = fields.Float(string="Costo")
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()

    @api.constrains('costo')
    def _check_something_costo_nomen(self):
        for record in self:
            if record.costo < 0:
                raise ValidationError('El costo debe ser positivo!')

    @api.constrains('fecha_inicio','fecha_fin')
    def _check_two_date_comp_costo_nomen(self):
        for record in self:
                if (record.fecha_fin):
                    start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                    end_date = record.fecha_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")


    def actualizar_costos_nomenclador_valor(self):
        nomencladores = self.env['hcd.nomenclador_costo'].browse(self._context.get('active_ids',[]))
        for nomenclador in nomencladores:
            
            dic = {
                'nomenclador_id' : nomenclador.id,
                'fecha_inicio' : nomenclador.fecha_vigencia_costo,
                'fecha_fin' : self.fecha_inicio,
                'costo' : nomenclador.costo
            }
            nomenclador.update({'costo': self.costo})
            nomenclador.update({'fecha_vigencia_costo': self.fecha_inicio})
            self.env['hcd.vigencia_costo_nomenclador'].create(dic)   

        return True
