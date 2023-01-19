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

def busco_costo_nomenclador(self,nomenclador_id):
    for rec in self:
        costo = 0
        complejidad = None
        discapacidad = None
        paliativo = None
        tipo_paciente = None
        zona_id = None
        if ( self.plan_id.paciente_id ):
            tipo_paciente = self.plan_id.paciente_id.tipo_paciente
            complejidad = self.plan_id.paciente_id.complejidad
            paliativo = self.plan_id.paciente_id.paliativo_paciente
            discapacidad = self.plan_id.paciente_id.discapacidad
            zona_id = self.plan_id.paciente_id.zona_costos_id
        else:
            raise ValidationError("No se encontró el paciente")

        if not (complejidad and discapacidad and paliativo and tipo_paciente and zona_id):
            raise ValidationError("Faltan variables de paciente para calcular el costo")
        # if cliente:   
        #     if  (not busco_variables_cliente(self,cliente.id)):
        #         discapacidad = None  
        #         complejidad = None
        #     else:
        #         discapacidad = cliente.discapacidad
        #         complejidad = cliente.complejidad
        
        categoria_id = nomenclador_id.categoria_id.id
        categoria_nomenclador= self.env['hcd.categoria_nomenclador'].search([('id','=',categoria_id)])
        titulo = categoria_nomenclador.titulo_defecto_id
     
        _logger.info("Buscando costos en Plan TRabajo Line : ................")
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
            ('zona_costos_id', '=', zona_id.id),      #los que siguen son por defecto , no asociados al paciente , y sin definir en esta instancia
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

def busco_variables_cliente(self,cliente_id):
    _logger.info("Entro en buscar variable de cliente:")
    _logger.info(cliente_id)
    complejidad=False
    if cliente_id:
        cliente_encontrado = self.env['res.partner'].search([('id','=',cliente_id)])
        if(cliente_encontrado):
            _logger.info("Cliente encontrado ...... .................")
            complejidad=cliente_encontrado.cliente_complejidad
    #discapacidad=False
    return(complejidad)


class PlanTrabajoLine(models.Model):
    _name = "hcd.plan_trabajo_line"
    _description = "Plan de Trabajo Line"
    name = fields.Char()

    dias_ids = fields.Many2many('hcd.dia.semana', string="Dias")

    fechas_seleccionadas = fields.Char()
       
    fecha_aux_ini = fields.Date(string="Fec.Ini.")
    fecha_aux_fin = fields.Date(string="Fec.Fin")
 
    plan_id = fields.Many2one('hcd.plan_trabajo', string='Plan de Referencia', required=True, copy=False)

    product_id = fields.Many2one(
        'product.template', string='Product Template',
    )
    cantidad = fields.Integer(default=1)   # cantidad de prestaciones
    cantidad_total = fields.Integer("Cant. Total")
    cantidad_realizadas = fields.Integer("Cant. Realizadas")
    porcentaje_realizado = fields.Float(compute="_calculo_porcentaje_realizado")
    cantidad_horas = fields.Integer(default=1)
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

    # esquema = fields.Selection([
    #     ('esquema1', 'Esquema 1'),
    #     ('esquema2', 'Esquema 2'),
    #     ('esquema3', 'Esquema 3')
    #     ],
    #     help="Esquemas ...")

    hora_inicio = fields.Integer(default=8) # agregar validacion <24
    hora_fin = fields.Integer() # agregar validacion <24
    prestador_id = fields.Many2one(
        'res.partner', 'Efector',
        domain="['|','|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector'),('hcd_type', '=', 'tecnico'),('status', '=', 'activo')]",
        help='Prestador asignado'
    )

    proveedor_id = fields.Many2one(
        'res.partner', 'Proveedor',
        domain="[('hcd_type', '=', 'proveedor'),('status', '=', 'activo')]",
        help='Proveedor asignado'
    )

    estado = fields.Selection([
         ('asignado', 'Asignado'),
         ('no_asignado', 'No asignado'),
         ('indefinido', 'indefinido'),
         ('modificado', 'Modificado'),
         ('agendado', 'Agendado'),
         ('primer_visita', 'Primer Visita'),
         ('rechazado', 'Rechazado'),],
         default='no_asignado',)

    agenda_ids = fields.One2many('hcd.agenda', 'plan_trabajo_line_id',
         string="Agenda",
    )

    precio = fields.Float("Precio")
    costo = fields.Float("Costo")

    pagador_id = fields.Many2one(
        'res.partner', 'Pagador',)

    observaciones = fields.Char()
    calculo_cantidad = fields.Boolean()
    nro_autorizacion = fields.Char("Nro. Autorización")

    codigo_modulo_pami = fields.Char("codigo del modulo_pami")
    descripcion_view = fields.Html(compute="_get_descripcion_producto_ptl")
    categoria_view = fields.Char(compute="_get_categoria_producto_ptl")
    nro_op_pami = fields.Char("Nro de op Pami")
    duracion = fields.Integer("duracion de la prestacion",default=1)

    @api.depends('product_id')
    def _get_descripcion_producto_ptl(self):
        for rec in self:
            if rec.product_id:
                rec.descripcion_view = rec.product_id.description
            else:
                rec.descripcion_view = ''

    @api.onchange('product_id')   #le agrego precios y costos
    def _get_categoria_producto_ptl(self):
        for rec in self:
            if rec.product_id:
                rec.categoria_view = rec.product_id.hcd_categ_prod
                rec.precio = rec.product_id.list_price
                rec.costo = rec.product_id.costo
                if (rec.product_id.hcd_categ_prod == 'servicio'):
                    nomenclador_id= rec.product_id.nomenclador_id
                    rec.costo = busco_costo_nomenclador(self,nomenclador_id) 
            else:
                rec.categoria_view = ''

    @api.onchange('cantidad_realizadas')
    def _calculo_porcentaje_realizado(self):
        for rec in self:
            rec.porcentaje_realizado = 0
            if  (rec.cantidad_total) and (rec.cantidad_total !=0) and (rec.cantidad_realizadas):
                rec.porcentaje_realizado = (rec.cantidad_realizadas / rec.cantidad_total) * 100



    @api.onchange('calculo_cantidad')
    def on_change_cantidad_prestacion_pt(self):
        cantidad = 1  #cantidad por defecto
        for rec in self:
            if  rec.fecha_aux_ini and rec.fecha_aux_fin and rec.frecuencia:
                cantidad = calculo_cantidad_de_prestaciones(self,rec.cantidad,rec.frecuencia,rec.fecha_aux_ini,rec.fecha_aux_fin)
        rec.cantidad_total = cantidad


    @api.onchange('fecha_aux_fin')
    def _check_two_date_fin_pt_line(self):
        fecha_fin=self.plan_id.fecha_fin.strftime('%Y-%m-%d')
        for record in self:
                if (record.fecha_aux_ini) and (record.fecha_aux_fin):
                    start_date = record.fecha_aux_ini.strftime('%Y-%m-%d')
                    end_date = record.fecha_aux_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
                    if end_date > fecha_fin:
                        raise ValidationError("La fecha de fin no puede ser mayor a la fecha de fin de la OP")
    
    
    @api.onchange('fecha_aux_ini')
    def _check_two_date_ini_pt_line(self):
        if not self.plan_id.fecha_inicio or not self.plan_id.fecha_fin:
            raise ValidationError("Debe selecccionar fechas de inicio y fin")
        fecha_inicio=self.plan_id.fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin=self.plan_id.fecha_fin.strftime('%Y-%m-%d')
        
        
        for record in self:
                if (record.fecha_aux_ini) and (record.fecha_aux_fin):
                    start_date = record.fecha_aux_ini.strftime('%Y-%m-%d')
                    end_date = record.fecha_aux_fin.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")
                    if start_date < fecha_inicio:
                        raise ValidationError("La fecha de inicio no puede ser menor a la fecha de inicio de la OP")


    @api.onchange('hora_inicio')
    def _check_hora_inicio_pt_line(self):
        for rec in self:
            if rec.hora_inicio < 0 or  rec.hora_inicio > 24:
                raise ValidationError("La hora de inicio está fuera de rango")


    @api.onchange('cantidad_horas')
    def _check_cantidad_horas_pt_line(self):
        for rec in self:
            if rec.cantidad_horas < 0 or rec.cantidad_horas > 30:
                raise ValidationError("La cantida de horas está fuera de rango")

    def viaticos(self):
        for applicant in self:
            plan_id = applicant.id
            if applicant.prestador_id:
                paciente_id = applicant.plan_id.paciente_id
                prestador_id = applicant.prestador_id
                _logger.info("Plan id : ..................." )
                _logger.info(plan_id)
                return {
                'name': _('Viáticos'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model':'hr.expense',
                # 'domain': [('paciente_id', '=' , paciente_id)],
                'context': {'default_paciente_id': paciente_id.id, 'default_prestador_id': prestador_id.id, 'default_plan_trabajo_line_id':plan_id},
            }           