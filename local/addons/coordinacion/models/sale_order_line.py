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




def validar_campos(cantidad_prestacion,frecuencia,start_date,end_date,dias_ids,fechas_seleccionadas,fecha_inicio,fecha_fin):
    if (cantidad_prestacion <= 0):
        raise ValidationError(_("la cantidad no puede se cero o negativa"))
    if( not frecuencia):
        raise ValidationError(_("Por favor seleccione una frecuencia valida"))
    if( not fecha_inicio):
        raise ValidationError(_("Por favor seleccione una fecha de inicio  OP"))
    if( not fecha_fin):
        raise ValidationError(_("Por favor seleccione una fecha de fin  OP"))
    if( frecuencia == SEMANAL and not dias_ids):
        raise ValidationError(_("Debe seleccionar al menos un dia para la frecuencia semanal"))
    if( (frecuencia == QUINCENAL or frecuencia == MENSUAL) and not fechas_seleccionadas):
        raise ValidationError(_("Debe seleccionar una fecha para la frecuencia seleccionada"))
    if start_date.strftime('%Y-%m-%d') > end_date.strftime('%Y-%m-%d'):
        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
    if start_date.strftime('%Y-%m-%d') < fecha_inicio.strftime('%Y-%m-%d'):
        raise ValidationError("La fecha de inicio no puede ser menor a la fecha de inicio de la OP")
    if end_date.strftime('%Y-%m-%d') > fecha_fin.strftime('%Y-%m-%d'):
        raise ValidationError("La fecha de fin no puede ser mayor a la fecha de fin de la OP")


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


def busco_costo_nomenclador(self,nomenclador_id):
    for rec in self:
        costo = 0
        #cliente = rec.partner_id
        categoria_id = nomenclador_id.categoria_id.id
        categoria_nomenclador= self.env['hcd.categoria_nomenclador'].search([('id','=',categoria_id)])
        
        titulo = categoria_nomenclador.titulo_defecto_id

        _logger.info("titulo : ................")
        _logger.info(titulo)

        complejidad = rec.complejidad_costo
        discapacidad = rec.discapacidad_costo
        paliativo = rec.paliativo   #  ojo , va a aplicar solo si es paciente ... 
        tipo_paciente = rec.tipo_paciente
        zona_id = self.zona_costos_id.id
        _logger.info("complejidad : ................")
        _logger.info(complejidad)
        _logger.info("discapacidad : ................")
        _logger.info(discapacidad)
        _logger.info("titulo : ................")
        _logger.info(titulo.id)
        _logger.info("zona de costos : ................")
        _logger.info(zona_id)
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
        
        if nomenclador_costo:      #  revisar si hace falta !!!  es por el error de Matias Badia
            for noc in nomenclador_costo:
                _logger.info("Costo Nomenclador encontrado: ................")
                _logger.info(nomenclador_costo)
                #costo = nomenclador_costo.costo
                costo = noc.costo
    return costo


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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    

    name = fields.Html()
    dias_ids = fields.Many2many('hcd.dia.semana', string="Dias")
    fechas_seleccionadas = fields.Char()
    frecuencia = fields.Selection([
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'mensual'),
        ('lunesAviernes', 'Lunes a Viernes'),
        ('sadofe', 'SADOFE'),
        ('cada48', 'Cada 48hs'),
        ('cada72', 'Cada 72hs')],
        help="Frecuencia del Servicio")
        
    cantidad_prestacion = fields.Integer("Cantidad", default=1)
    costo_prestacion = fields.Float("Costo")
    calculo_cantidad = fields.Boolean()
    descripcion_view = fields.Html(compute="on_change_descripcion_producto")
    
    # los agrego para poder calcular el costo del nomenclador 
    partner_id = fields.Many2one('res.partner', string='Customer')    
    
    tipo_paciente = fields.Selection([
        ('ADULTO', 'ADULTO'),
        ('PEDIATRICO', 'PEDIATRICO'),
        ('NEONATO', 'NEONATO'),],
        help="Tipo de paciente según su edad")  
        
    paliativo = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    complejidad = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ])

    complejidad_costo = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ])
    
    discapacidad = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])
    
    discapacidad_costo = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    zona_costos_id = fields.Many2one(
        comodel_name="hcd.zona_costos",
        string="Zona de costos",
    )
    dia_habil = fields.Selection([
        ('H', 'HABIL'),
        ('N', 'NO HABIL'),
        ], default='H')

    #lo agrego para utilizar MarkUp
    utilizar_mu = fields.Boolean("Utilizando MarkUp")
    mu_servicio = fields.Integer("MarkUp rrhh")
    mu_equipo = fields.Integer("MarkUp equipo")
    mu_insumo = fields.Integer("MarkUp insumo")
    nro_autorizacion = fields.Char("Nro. Autorización")


    @api.onchange('costo_prestacion')
    def on_change_costo_prestacion(self):
        _logger.info("Entro en cambio de costo prestacion .................")
        for rec in self:
            if (rec.mu_servicio != 0) or (rec.mu_equipo != 0) or (rec.mu_insumo != 0):  
                _logger.info("Entro a modificar en  cambio de costo prestacion .................")
                precio_unitario = rec.product_template_id.list_price
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'servicio'):
                    if rec.mu_servicio != 0:
                        _logger.info("Entro en  MarkUp servicio: .................")
                        _logger.info(rec.mu_servicio)
                        porcentaje = (100 + rec.mu_servicio)/100
                        _logger.info("Entro en  mu_servicio  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (rec.costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)
                    
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'equipamiento'):
                    if rec.mu_equipo != 0:
                        _logger.info("Entro en  MarkUp equipo: .................")
                        _logger.info(rec.mu_equipo)
                        porcentaje = (100 + rec.mu_equipo)/100
                        _logger.info("Entro en  mu_equipo  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (rec.costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)
                    
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'material'):
                    if rec.mu_insumo != 0:
                        _logger.info("Entro en  MarkUp: .................")
                        _logger.info(rec.mu_insumo)
                        porcentaje = (100 + rec.mu_insumo)/100
                        _logger.info("Entro en  mu_insumo  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (rec.costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)


                _logger.info("Salio del if , antes de romper ....")
                _logger.info(precio_unitario)
                rec.product_template_id.list_price = precio_unitario  # no se porque ... 
                rec.price_unit = rec.product_template_id.list_price
                rec.name = rec.product_template_id.description
                _logger.info("termina onchange de costo prestacion  ....")

    
    @api.depends('product_template_id')
    def on_change_descripcion_producto(self):
        for rec in self:
            rec.descripcion_view = ''
            if rec.product_template_id:
                rec.descripcion_view = rec.product_template_id.description
    
    @api.onchange('product_template_id')
    def on_change_producto(self):
        # paciente = self.partner_id   ME FALTA EL RES_PARTNER DEL PPTO
        # _logger.info("Paciente  : .................")
        # _logger.info(paciente)
        for rec in self:
            rec.descripcion_view = ''
            if rec.product_template_id:
                id = rec.product_template_id.id
                rec.product_id = self.env['product.product'].search([('product_tmpl_id', '=', id)])
                _logger.info("Product Product  : .................")
                _logger.info(rec.product_id)
                rec.name = rec.product_template_id.description   # pongo esto para que muestre la descripcion en name
                
            if rec.product_template_id and rec.product_template_id.list_price:
                precio_unitario = rec.product_template_id.list_price
                costo_prestacion = rec.product_template_id.costo
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'servicio'):
                    nomenclador_id= rec.product_template_id.nomenclador_id
                    costo_prestacion = busco_costo_nomenclador(self,nomenclador_id)    # va a buscar costo , si es Servicio!!!
                    if rec.mu_servicio != 0:
                        _logger.info("Entro en  MarkUp: .................")
                        _logger.info(rec.mu_servicio)
                        porcentaje = (100 + rec.mu_servicio)/100
                        _logger.info("Entro en  mu_servicio  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)
                   
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'equipamiento'):
                    if rec.mu_equipo != 0:
                        _logger.info("Entro en  MarkUp: .................")
                        _logger.info(rec.mu_equipo)
                        porcentaje = (100 + rec.mu_equipo)/100
                        _logger.info("Entro en  mu_equipo  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)
                   
                if rec.product_template_id and (rec.product_template_id.hcd_categ_prod == 'material'):
                    if rec.mu_insumo != 0:
                        _logger.info("Entro en  MarkUp: .................")
                        _logger.info(rec.mu_insumo)
                        porcentaje = (100 + rec.mu_insumo)/100
                        _logger.info("Entro en  mu_insumo  Porcentaje : ..................")
                        _logger.info(porcentaje)

                        precio_unitario = round (costo_prestacion * porcentaje, 2)
                        _logger.info(precio_unitario)


                _logger.info("Salio del if  onchange producto....")
                _logger.info(precio_unitario)
                rec.costo_prestacion = costo_prestacion
                rec.product_template_id.list_price = precio_unitario  # no se porque ... 
                _logger.info("despues de modificar  precio unitario....")
                rec.price_unit = rec.product_template_id.list_price
                rec.name = rec.product_template_id.description

                rec.descripcion_view = rec.product_template_id.description
            

    @api.onchange('start_date')
    def on_change_start_date(self):
        for rec in self:
            fecha_inicio=self.order_id.default_start_date
            fecha_fin=self.order_id.default_end_date
            if not fecha_inicio or not fecha_fin:
                raise ValidationError("Debe selecccionar fechas de inicio y fin de la OP")
            else:
                if rec.start_date:
                    if rec.start_date > fecha_fin or rec.start_date < fecha_inicio:
                        raise ValidationError("La fecha de inicio está fuera de la ventana de la OP")

    @api.onchange('end_date')
    def on_change_end_date(self):
        for rec in self:
            fecha_inicio=self.order_id.default_start_date
            fecha_fin=self.order_id.default_end_date
            if not fecha_inicio or not fecha_fin:
                raise ValidationError("Debe selecccionar fechas de inicio y fin de la OP")
            else:
                if rec.end_date:
                    if rec.end_date > fecha_fin or rec.end_date < fecha_inicio:
                        raise ValidationError("La fecha de finalización está fuera de la ventana de la OP")

    @api.onchange('calculo_cantidad')
    def on_change_cantidad_prestacion(self):
        cantidad = 1  #cantidad por defecto
        for rec in self:
            fecha_inicio=self.order_id.default_start_date
            fecha_fin=self.order_id.default_end_date
            if  rec.start_date and rec.end_date and rec.frecuencia:
                validar_campos(rec.cantidad_prestacion,rec.frecuencia,rec.start_date,rec.end_date,rec.dias_ids, rec.fechas_seleccionadas,fecha_inicio,fecha_fin)
                cantidad = calculo_cantidad_de_prestaciones(self,rec.cantidad_prestacion,rec.frecuencia,rec.start_date,rec.end_date)
        rec.product_uom_qty = cantidad
    #         if  rec.start_date and rec.end_date:
    #             start_date = rec.start_date.strftime('%Y-%m-%d')
    #             end_date = rec.end_date.strftime('%Y-%m-%d')
    #             if start_date > end_date:
    #                 rec.start_date = rec.end_date
    #                 raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
    #         if rec.frecuencia and rec.start_date and rec.end_date:
    #             #validar_campos(rec.cantidad_prestacion,rec.frecuencia,rec.start_date,rec.end_date,rec.dias_ids, rec.fechas_seleccionadas)
        


 
            
