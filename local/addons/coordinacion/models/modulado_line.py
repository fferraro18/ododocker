from ast import Str
from time import strftime
from odoo import api,fields, models, _
from odoo.exceptions import ValidationError
import datetime
import logging
_logger = logging.getLogger(__name__)

DIARIA = 'diaria'   #todos los días
SEMANAL = 'semanal'
QUINCENAL = 'quincenal'
MENSUAL = 'mensual'
CADA48 = 'cada48'   # cada 48 hs , todods los días desde fecha_inicio y con delta (days=2)
CADA72 = 'cada72'   # cada 72 hs , todods los días desde fecha_inicio y con delta (days=3)
LUNVIER = 'lunesAviernes'
SABDOM = 'sadofe'     # Sab y Dom  Falta cargar una lista de feriados y chequear contra dicha lista

DIAS_SEMANA = ['1','2','3','4','5']
SAB_DOM = ['6','7']

def calculo_cantidad_de_prestaciones (self,cantidad_prestacion,frecuencia,fecha_inicio,fecha_fin):
    delta = datetime.timedelta(days=1)
    if frecuencia == CADA48:
        delta = datetime.timedelta(days=2)
    if frecuencia == CADA72:
        delta = datetime.timedelta(days=3)
    fecha_actual = fecha_inicio
    contador = 0
    while fecha_actual <= fecha_fin:
        cumpleCondicion = False
        if (frecuencia == DIARIA) | (frecuencia == CADA48) | (frecuencia == CADA72):
            contador = contador + cantidad_prestacion   
        elif frecuencia == SEMANAL:
            cumpleCondicion = cumple_condicion_semanal_obj(fecha_actual, self.dias_ids)
            if cumpleCondicion:
                contador = contador + cantidad_prestacion 
        elif frecuencia == LUNVIER:
            cumpleCondicion = cumple_condicion_semanal(fecha_actual, DIAS_SEMANA)
            if cumpleCondicion:
                contador = contador + cantidad_prestacion 
        elif frecuencia == SABDOM:
            cumpleCondicion = cumple_condicion_semanal(fecha_actual, SAB_DOM)
            if cumpleCondicion:
                contador = contador + cantidad_prestacion 
        elif (frecuencia == QUINCENAL) | (frecuencia == MENSUAL):
            cumpleCondicion = cumple_condicion_quincenal(fecha_actual, self.fechas_seleccionadas)
            if cumpleCondicion:
                contador = contador + cantidad_prestacion 
        
        fecha_actual += delta
    #self.product_uom_qty = contador
    return contador

def cumple_condicion_semanal (fecha,condicion):
    _logger.info("cumple condicion Semanal")
    for dia_selecionado in condicion:
        #_logger.info("dia seleccionado" )
        #_logger.info(dia_selecionado)
        #_logger.info( "dia actual" + str(fecha.isoweekday()))
        if ( str(fecha.isoweekday()) == dia_selecionado ):
            return True
    return False

def cumple_condicion_semanal_obj (fecha,condicion):
    _logger.info("cumple condicion Semanal    OBJ")
    for dia_seleccionado in condicion:
        _logger.info("dia seleccionado:............." )
        _logger.info(dia_seleccionado)
        #s = [int(s) for s in str.split(dia_seleccionado.id) if s.isdigit()]
        _logger.info(dia_seleccionado._origin.id)
        _logger.info( "dia actual" + str(fecha.isoweekday()))
        if ( fecha.isoweekday() == dia_seleccionado._origin.id ):
            return True
    return False

def cumple_condicion_quincenal(fecha, condicion):
    for dia_condicion in condicion.split(","):
        dia_seleccionado = datetime.datetime.strptime(dia_condicion, '%d/%m/%Y')
        if fecha == dia_seleccionado.date():
            #_logger.info("Fecha encontrada" + str(fecha))
            return True
    #_logger.info("Fecha no encontrada")
    return False

class ModuladoLine(models.Model):
    _name = "hcd.modulado_line"
    _description = "Modulado Line"
    name = fields.Char()
 
    modulado_id = fields.Many2one('hcd.modulado', string='Modulado de Referencia', required=True, copy=False)

    product_id = fields.Many2one(
        'product.template', string='Product Template'
    )

    descripcion_view = fields.Html(compute="_get_descripcion_producto_ml", string="Descripción")

    dias_ids = fields.Many2many('hcd.dia.semana', string="Dias")
    fechas_seleccionadas = fields.Char()    
    fecha_aux_ini = fields.Date(string="Fec.Ini.")
    fecha_aux_fin = fields.Date(string="Fec.Fin")
    precio = fields.Float("Precio")
    precio_referencia = fields.Float("Precio de referencia")
    porcentaje = fields.Integer('Porcentaje')
    costo_referencia = fields.Float("Costo Ref")
    costo = fields.Float("Costo")
    
    cantidad = fields.Integer(default=1)
    cantidad_total = fields.Integer("Cant. Total")
    cant_max_mensual = fields.Integer("Cant. máxima")
    calculo_cantidad = fields.Boolean(default=False)
    
    cod_practica_cli = fields.Char("Código de práctica")    
    desc_practica_cli = fields.Char("Desc de práctica") 

    frecuencia = fields.Selection([
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'mensual'),
        ('lunesAviernes', 'Lunes a Viernes'),
        ('sadofe', 'SADOFE'),
        ('cada24', 'Cada 24hs'),
        ('cada48', 'Cada 48hs'),
        ('cada72', 'Cada 72hs')],
        help="Frecuencia del Servicio")

    dia_habil = fields.Selection([
        ('H', 'HABIL'),
        ('N', 'NO HABIL'),
        ],default='H')
 

    @api.onchange('calculo_cantidad')
    def on_change_cantidad_prestacion_ml(self):
        cantidad = 1  #cantidad por defecto
        for rec in self:
            if  rec.fecha_aux_ini and rec.fecha_aux_fin and rec.frecuencia:
                cantidad = calculo_cantidad_de_prestaciones(self,rec.cantidad,rec.frecuencia,rec.fecha_aux_ini,rec.fecha_aux_fin)
        rec.cantidad_total = cantidad


    @api.onchange('fecha_aux_ini')
    def _check_two_date_ini_mod_line(self):
        if (self.modulado_id.utilizar_vigencia) and (not self.modulado_id.vigencia_desde or not self.modulado_id.vigencia_hasta):
            raise ValidationError("Debe selecccionar fechas de inicio y fin")
        
        if (self.modulado_id.utilizar_vigencia):
            for record in self:
                    fecha_inicio=self.modulado_id.vigencia_desde.strftime('%Y-%m-%d')
                    if (record.fecha_aux_ini) and (record.fecha_aux_fin):
                        start_date = record.fecha_aux_ini.strftime('%Y-%m-%d')
                        end_date = record.fecha_aux_fin.strftime('%Y-%m-%d')
                        if start_date > end_date:
                            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
                        if start_date < fecha_inicio:
                            raise ValidationError("La fecha de inicio no puede ser menor a la fecha de inicio del modulado")

    @api.onchange('fecha_aux_fin')
    def _check_two_date_fin_mod_line(self):
        if (self.modulado_id.utilizar_vigencia):
            for record in self:
                    fecha_fin=self.modulado_id.vigencia_hasta.strftime('%Y-%m-%d')
                    if (record.fecha_aux_ini) and (record.fecha_aux_fin):
                        start_date = record.fecha_aux_ini.strftime('%Y-%m-%d')
                        end_date = record.fecha_aux_fin.strftime('%Y-%m-%d')
                        if start_date > end_date:
                            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
                        if end_date > fecha_fin:
                            raise ValidationError("La fecha de fin no puede ser mayor a la fecha de fin del modulado")


    @api.depends('product_id')
    def _get_descripcion_producto_ml(self):
        for rec in self:
            if rec.product_id:
                rec.descripcion_view = rec.product_id.description
            else:
                rec.descripcion_view = ''