# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
import string
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


def busca_excepcion_costo(self,prestador_id,paciente_id,nomenclador_id,fecha_actual):
    costo=0
    
    excepciones = self.env['hcd.excepcion_costo_prestador'].search([
                    ('prestador_id.id', '=', prestador_id),('fecha_ini', '<=', fecha_actual),('fecha_fin', '>=', fecha_actual),])
    
    for excepcion in excepciones:
        _logger.info("Entro en Excepcion con prestador ID  y nomenclador ID....................:")   # son cuatro combinaciones , 2 IF anidados
        _logger.info(prestador_id)
        _logger.info(nomenclador_id)
        _logger.info(excepcion.precio_base)
        if excepcion.paciente_id:
            if excepcion.nomenclador_id:
                if excepcion.paciente_id.id == paciente_id and excepcion.nomenclador_id.id == nomenclador_id:
                    _logger.info("excepcion con paciente Y nomenclador ")
                    costo = excepcion.precio_base
            else:
                if excepcion.paciente_id.id == paciente_id:
                    _logger.info("excepcion con paciente sin nomenclador ")
                    costo = excepcion.precio_base
        else:
            if excepcion.nomenclador_id:
                if excepcion.nomenclador_id.id == nomenclador_id:
                    _logger.info("excepcion sin paciente  con  nomenclador ")
                    costo = excepcion.precio_base
            else:
                _logger.info("excepcion sin paciente ni nomenclador ")
                costo = excepcion.precio_base
    return costo

def busco_costo_nomenclador(self,nomenclador_id,paciente):
    costo = 0
    categoria_id = nomenclador_id.categoria_id.id
    categoria_nomenclador= self.env['hcd.categoria_nomenclador'].search([('id','=',categoria_id)])
    titulo = categoria_nomenclador.titulo_defecto_id


    complejidad = paciente.complejidad
    discapacidad = paciente.discapacidad
    paliativo = paciente.paliativo_paciente 
    tipo_paciente = paciente.tipo_paciente
    zona_id = paciente.zona_costos_id.id
    _logger.info("complejidad : ................")
    _logger.info(complejidad)
    nomenclador_costo = self.env['hcd.nomenclador_costo'].search([
        ('nomenclador_id', '=', nomenclador_id.id),
        ('tipo_paciente', '=', tipo_paciente),
        ('complejidad', '=', complejidad),
        ('discapacidad', '=', discapacidad),
        ('paliativo', '=', paliativo),
        ('zona_costos_id', '=', zona_id),      #los que siguen son por defecto , no asociados al paciente , y sin definir en esta instancia
        ('profesion_id', '=', titulo.id),
        ('dia_habil', '=', 'H'),
        ('dispo_horaria','=', 'DIURNA')   
        ])
    _logger.info("Costo Nomenclador encontrado: ................")
    _logger.info(nomenclador_costo)   
    if nomenclador_costo:
        costo = nomenclador_costo.costo
    return costo



class RecalcularCostoAgenda(models.TransientModel):
    _name = 'hcd.recalcular.costo.agenda'
    _description = "Recalcular"


    def recalcular_costo_agenda(self):
        agendas = self.env['hcd.agenda'].browse(self._context.get('active_ids',[]))
        for agenda in agendas:
            costo_prestacion=agenda.costo_prestacion     # valores originales
            precio_prestacion=agenda.precio_prestacion
            if agenda.producto_id and (agenda.producto_id.hcd_categ_prod == 'servicio'):
                nomenclador_id= agenda.producto_id.nomenclador_id
                costo_nomenclador = busco_costo_nomenclador(self,nomenclador_id,agenda.paciente_id)    # va a buscar costo , si es Servicio!!!
                if costo_nomenclador != 0:                  #  encontro costo en la lista de costos
                    costo_prestacion = costo_nomenclador
                    _logger.info("Encontro costo en lista de costos !!  ")



            if agenda.prestador_id:     #voy a buscar si hay excepciones de costos para el prestador
                bandera = False
                prestador_id = agenda.prestador_id.id
                paciente_id = agenda.paciente_id.id
                fecha= agenda.fecha_visita.date()
                costo_excepcion = busca_excepcion_costo(self,prestador_id,paciente_id,nomenclador_id.id,fecha)
                if costo_excepcion !=0:
                    _logger.info("encontro excepcion del prestador!!  .................")
                    costo_prestacion = costo_excepcion


            if agenda.producto_id:                 #  voy a buscar el precio y el costo, para cualquier tipo producto 
                producto = self.env['product.template'].search([('id','=',agenda.producto_id.id)])
                if producto:
                    precio_prestacion = producto.list_price
                    costo_prestacion = producto.costo


            _logger.info("entra a actualizar Costo y Precio:  .................")
            agenda.update({'costo_prestacion': costo_prestacion,'precio_prestacion': precio_prestacion})



        return True


