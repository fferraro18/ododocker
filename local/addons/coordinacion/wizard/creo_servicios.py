# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class CreoServicios(models.TransientModel):
    _name = 'hcd.creo.servicios'
    _description = "Crear Servicios por OS"

    obra_social_id = fields.Many2one(
        'res.partner', 'Obra Social',
        domain="[('hcd_type', '=', 'cliente')]",
        help='Obra social'
    )

    def creo_servicios(self):    
        obrasocial_id = self.obra_social_id.id
        obrasocial = self.obra_social_id.name

        nomencladores = self.env['hcd.nomenclador']
        nomencladores_ids = nomencladores.search([])
        for nomenclador in nomencladores_ids:
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.1.1',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'ADULTO',
                'paliativo' : 'SI',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.0.1',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'ADULTO',
                'paliativo' : 'NO',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.1.2',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'PEDIATRICO',
                'paliativo' : 'SI',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.0.2',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'PEDIATRICO',
                'paliativo' : 'NO',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.1.3',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'NEONATO',
                'paliativo' : 'SI',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
            dic = {
                'name' : obrasocial + '.' + nomenclador.name + '.0.3',
                'nomenclador_id' : nomenclador.id,
                'obra_social_id' : obrasocial_id,
                'tipo_paciente' : 'NEONATO',
                'paliativo' : 'NO',
                'fecha_inicio' : datetime.now(),
                'list_price' : 1,
                'hcd_categ_prod' : 'servicio',
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
            }
            _logger.info("%s", str(dic))
            self.env['product.template'].create(dic)
        return True
