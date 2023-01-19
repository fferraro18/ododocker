# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ActualizoCostos(models.TransientModel):
    _name = 'hcd.actualizo.costos.nomenclador'
    _description = "Actualizo costos nomenclador"

    porcentaje = fields.Float(string="porcentaje")
    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()

    @api.constrains('fecha_inicio','fecha_fin')
    def _check_two_date_comp_nomen(self):
        for record in self:
                if (record.fecha_fin):
                    start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                    end_date = record.fecha_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    def actualizar_costos_nomenclador(self):
        nomencladores = self.env['hcd.nomenclador_costo'].browse(self._context.get('active_ids',[]))
        for nomenclador in nomencladores:
     
            dic = {
                'nomenclador_id' : nomenclador.id,
                'fecha_inicio' : nomenclador.fecha_vigencia_costo,
                'fecha_fin' : self.fecha_inicio,
                'costo' : nomenclador.costo
            }
            nuevo_costo = float(nomenclador.costo) * ((self.porcentaje/100) + 1)
            nomenclador.update({'costo': nuevo_costo})
            nomenclador.update({'fecha_vigencia_costo': self.fecha_inicio})
            self.env['hcd.vigencia_costo_nomenclador'].create(dic)     
            
        return True

