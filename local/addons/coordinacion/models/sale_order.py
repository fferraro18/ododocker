from odoo import api,fields, models
import datetime
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

DIARIA = 'diaria'   #todos los días
SEMANAL = 'semanal'
QUINCENAL = 'quincenal'
MENSUAL = 'mensual'
CADA48 = 'cada48'   # cada 48 hs , todods los días desde fecha_inicio y con delta (days=2)
CADA72 = 'cada72'   # cada 72 hs , todods los días desde fecha_inicio y con delta (days=3)
LUNVIER = 'lunesAviernes'
SABDOM = 'sabadoYdomingo'

DIAS_SEMANA = ['1','2','3','4','5']
SAB_DOM = ['6','7']

def generar_fecha_hora(fecha, hora_inicio):
    #TIME_ZONE_AR = 3
    delta_hr = datetime.timedelta(hours = 3)
    my_date = datetime.datetime(fecha.year, fecha.month, fecha.day, hora_inicio, 0, 0 ,0)
    my_date += delta_hr
    return my_date

def generar_agenda(self, fecha_inicio, fecha_fin, plan_id, paciente_id, coordinador_id, product_line):
    _logger.info("Entro con  la fecha  INICIAL:")
    _logger.info(fecha_inicio)
    frecuencia = product_line.frecuencia
    name = self.name
    delta = datetime.timedelta(days=1)
    if frecuencia == CADA48:
        delta = datetime.timedelta(days=2)
    if frecuencia == CADA72:
        delta = datetime.timedelta(days=3)
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        agregarRegistro = False
        if (frecuencia == DIARIA) | (frecuencia == CADA48):
            agregarRegistro = True        
        elif frecuencia == SEMANAL:
            agregarRegistro = cumple_condicion_semanal_obj(fecha_actual, product_line.dias_ids)
        elif frecuencia == LUNVIER:
            agregarRegistro = cumple_condicion_semanal(fecha_actual, DIAS_SEMANA)
        elif frecuencia == SABDOM:
            agregarRegistro = cumple_condicion_semanal(fecha_actual, SAB_DOM)
        elif (frecuencia == QUINCENAL) | (frecuencia == MENSUAL):
            agregarRegistro = cumple_condicion_quincenal(fecha_actual, product_line.fechas_seleccionadas)
        
        if(agregarRegistro):
            # prestador_id = product_line.prestador_id.id
            # costo_excepcion = busca_excepcion_costo(self,prestador_id)
            costo_excepcion = 0
            # if (costo_excepcion == 0):
            #     _logger.info("--------------------  el costo es :")
            #     _logger.info(product_line.costo)
            #     costo_excepcion = product_line.costo
            fecha_hora = generar_fecha_hora(fecha_actual,8)   #fijo la hora de inicio en 8:00  , es intrascendente pero necesaria
            dic_linea = {
                'name' : name,
                'plan_trabajo_id' : plan_id,
                'paciente_id' : paciente_id,
                'empleado_id' : coordinador_id,
                'plan_trabajo_line_id' : product_line.id,
                'fecha_visita' : fecha_hora,
                'duracion' : 1,                              #  fijo la duracion en 1hr
                'producto_id' : product_line.product_id.id,
                'nro_autorizacion' : product_line.nro_autorizacion,
                'costo_prestacion': costo_excepcion,
                'estado' : 'no_asignado'
            }
            _logger.info("Se va a guardar la agenda con la fecha:")
            _logger.info(fecha_hora.strftime("%m/%d/%Y, %H:%M:%S"))
            record_linea = self.env['hcd.agenda'].create(dic_linea)
            #agregar_registro_agenda(self, dic_linea)
        fecha_actual += delta

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
    for dia_selecionado in condicion:
        #_logger.info("dia seleccionado:............." )
        #_logger.info(dia_selecionado.id)
        #_logger.info( "dia actual" + str(fecha.isoweekday()))
        if ( fecha.isoweekday() == dia_selecionado.id ):
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

class SaleOrder(models.Model):
    _inherit = "sale.order"

    estado_pt = fields.Selection([
        ('SIN CREAR', 'SIN CREAR'),
        ('AGREGADO OP', 'AGREGADO OP'),
        ('CREADO', 'CREADO')],
        default='SIN CREAR',)

    nodo_id = fields.Many2one(
        comodel_name='hcd.nodo', string='Nodo',
        help='Nodo de pertenencia'
    )

    paga_paciente = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO')],
        default='NO',)


    utilizar_mu = fields.Boolean(default=False)
    mu_servicio = fields.Integer("MarkUp rrhh", default=0)
    mu_equipo = fields.Integer("MarkUp equipo", default=0)
    mu_insumo = fields.Integer("MarkUp insumo", default=0)
    #recalcular_mu = fields.Boolean()
    

    financiador_id = fields.Many2one(
        'res.partner', 'Financiador',
        domain="[('hcd_type', '=', 'cliente'),('cliente_estado','=','activo')]",
        help='Financiador'
    )
    obra_social_id_view = fields.Char(compute="_get_obra_social")
    partner_type_view = fields.Char(compute="_get_partner_type", default='Oportunidad')
    coordinador_id_view = fields.Char(compute="_get_coordinador")
    nodo_view = fields.Char(compute="_get_nodo")
    filtro_id = fields.Integer(compute="_get_filtro_id")     #  para filtrar los servicios 
    aux_start_date = fields.Date(compute="_get_start_date")
    aux_end_date = fields.Date(compute="_get_end_date")     #  para copiar en order_line  

    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        help='Paciente asociado al plan de trabajo'
    )

    op_ids = fields.One2many('hcd.plan_trabajo', 'paciente_id', store=False,
         string="OP activas del paciente",
    )

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
    
    discapacidad = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    complejidad_costo = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ])
    
    discapacidad_costo = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])
       
    porcentaje_vip = fields.Selection([
        ('10', '10'),
        ('20', '20'),
        ('30', '30'),
        ('40', '40'),
        ])

    zona_costos_id = fields.Many2one(
        comodel_name="hcd.zona_costos",
        string="Zona de costos",
    )

    # @api.onchange('mu_servicio')
    # def on_change_mu_servicio(self):
    #     for rec in self:
    #         if  rec.mu_servicio:
    #             if rec.mu_servicio <0 or rec.mu_servicio >100:
    #                 raise ValidationError("El MarkUp debe ser un valor entre 0 y 100")

    # @api.constrains('partner_id')
    # def check_type_view_inicial(self):
    #     for rec in self:
    #         if rec.partner_id and (rec.partner_id.hcd_type != None) and ( (rec.partner_id.hcd_type == 'paciente') or (rec.partner_id.hcd_type == 'cliente_paciente')):
    #             rec.partner_type_view = 'Cliente/Paciente'
    #             _logger.info("Entro en  seteo de Paciente ...... .................")
    #             rec.paciente_id = rec.partner_id
    #         elif rec.partner_id and (rec.partner_id.id != None) and (rec.partner_id.hcd_type != None):
    #             rec.partner_type_view = rec.partner_id.cliente_nivel
    #         else: 
    #             rec.partner_type_view = 'Oportunidad'

    @api.onchange('partner_id')
    def have_change(self):
        _logger.info("Se ejecuta el onchange de sale_order....")
        SaleOrder._get_variables_para_costo(self)
        SaleOrder._get_obra_social(self)
        SaleOrder._get_coordinador(self)
        SaleOrder._get_partner_type(self)
        SaleOrder._get_filtro_id(self)

    @api.onchange('nodo_id')
    def _get_nodo(self):
        for rec in self:
            if rec.nodo_id and (rec.nodo_id.id != None):
                rec.nodo_view = rec.nodo_id.name
            else:
                rec.nodo_view = 'Indefinido'

    @api.onchange('default_start_date')
    def _get_start_date(self):
        _logger.info("Antes del for :  AAAAAAAAAAAAAAAA....")
        for rec in self:
            _logger.info("Muestro rec en cambio start_date :  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX....")
            _logger.info(rec)
            if rec.default_start_date:
                rec.aux_start_date = rec.default_start_date


    @api.onchange('default_end_date')
    def _get_end_date(self):
        for rec in self:
            if rec.default_end_date:
                rec.aux_end_date = rec.default_end_date


    def _get_variables_para_costo(self):
        _logger.info("Se ejecuta el onchange de _get_variables_para_costo....")
        for rec in self:
            if rec.partner_id and (rec.partner_id.id != None):
                rec.tipo_paciente = rec.partner_id.tipo_paciente
                rec.paliativo = rec.partner_id.paliativo_paciente
                rec.zona_costos_id = rec.partner_id.zona_costos_id
                rec.complejidad_costo = rec.partner_id.complejidad
                rec.porcentaje_vip = rec.partner_id.porcentaje_vip
                rec.discapacidad_costo = rec.partner_id.discapacidad
                if rec.partner_id.obra_social_id:   
                    if  (not busco_variables_cliente(self,rec.partner_id.obra_social_id.id)):
                        rec.discapacidad = None  
                        rec.complejidad = None
                        rec.porcentaje_vip = None
                    else:
                        rec.discapacidad = rec.partner_id.discapacidad
                        rec.complejidad = rec.partner_id.complejidad
                        rec.porcentaje_vip = rec.partner_id.porcentaje_vip
                    
                rec.nodo_id = rec.partner_id.nodo_id
                if rec.nodo_id and (rec.nodo_id.id != None):
                    rec.nodo_view = rec.nodo_id.name
                else:
                    rec.nodo_view = 'Indefinido'

    
    def _get_obra_social(self):
        _logger.info("Se ejecuta el onchange de _get_obra_social....")
        for rec in self:
            if rec.partner_id and (rec.partner_id.id != None):
                rec.obra_social_id_view = rec.partner_id.obra_social_id.name

    
    def _get_coordinador(self):
        _logger.info("Se ejecuta el onchange de _get_coordinador....")
        for rec in self:
            if rec.partner_id and (rec.partner_id.coordinador_id != None):
                rec.coordinador_id_view = rec.partner_id.coordinador_id.name
            if rec.partner_id:
                op_anteriores = self.env['hcd.plan_trabajo'].search(['&',('paciente_id','=',rec.partner_id.id),('status','=','activo')])
                if(len(op_anteriores) > 0):
                    _logger.info("Tiene OP Activas !!!! ...... .................")
                    rec.op_ids = op_anteriores
                else:
                    _logger.info("NO Tiene OP Activas !!!! ...... .................")
                    rec.op_ids = None
    
    def _get_partner_type(self):
        _logger.info("Se ejecuta el onchange de _get_partner_type....")
        for rec in self:
            if rec.partner_id and (rec.partner_id.hcd_type != None) and ( (rec.partner_id.hcd_type == 'paciente') or (rec.partner_id.hcd_type == 'cliente_paciente')):
                rec.partner_type_view = 'Cliente/Paciente'
                _logger.info("Entro en  seteo de Paciente ...... .................")
                rec.paciente_id = rec.partner_id
            elif rec.partner_id and (rec.partner_id.id != None) and (rec.partner_id.hcd_type != None):
                rec.partner_type_view = rec.partner_id.cliente_nivel
            else: 
                rec.partner_type_view = 'Oportunidad'

    @api.onchange('financiador_id')
    def _get_filtro_financiador_id(self):
        for rec in self:
            rec.filtro_id = self.financiador_id.id

    
    def _get_filtro_id(self):
        _logger.info("Se ejecuta el onchange de _get_filtro_id....")
        for rec in self:
            id_privado = self.env['res.partner'].search(['&',('name','=','PRIVADO'),('hcd_type','=','cliente')])
            if not id_privado:
                raise ValidationError('Primero debe crear el Cliente PRIVADO')
            rec.filtro_id = 0
            if rec.partner_id:
                if (rec.partner_id.hcd_type == 'cliente') or (rec.paga_paciente == 'SI'):
                    rec.filtro_id = id_privado.id
                    rec.obra_social_id_view='PRIVADO'
                
                elif (rec.partner_id.obra_social_id):
                    rec.filtro_id = rec.partner_id.obra_social_id.id
                    rec.obra_social_id_view = rec.partner_id.obra_social_id.name
                elif (rec.financiador_id):
                    rec.filtro_id = rec.financiador_id.id
                    rec.obra_social_id_view = rec.financiador_id.name
                  
                if  (not busco_variables_cliente(self,rec.filtro_id)):
                    rec.discapacidad = None  
                    rec.complejidad = None
                    rec.porcentaje_vip = None
                else:
                    rec.discapacidad = rec.partner_id.discapacidad
                    rec.complejidad = rec.partner_id.complejidad
                    rec.porcentaje_vip = rec.partner_id.porcentaje_vip

    @api.onchange('paga_paciente')
    def _get_filtro_id_cambio(self):
        for rec in self:
            id_privado = self.env['res.partner'].search(['&',('name','=','PRIVADO'),('hcd_type','=','cliente')])
            if not id_privado:
                raise ValidationError('Primero debe crear el Cliente PRIVADO')
            rec.filtro_id = 0
            if rec.partner_id:
                if (rec.paga_paciente == 'SI'):
                    rec.filtro_id = id_privado.id
                    rec.obra_social_id_view='PRIVADO'
                
                elif (rec.partner_id.obra_social_id):
                    rec.filtro_id = rec.partner_id.obra_social_id.id
                    rec.obra_social_id_view = rec.partner_id.obra_social_id.name
                elif (rec.financiador_id):
                    rec.filtro_id = rec.financiador_id.id
                    rec.obra_social_id_view = rec.financiador_id.name
                
                if  (not busco_variables_cliente(self,rec.filtro_id)):
                    rec.discapacidad = None  
                    rec.complejidad = None
                    rec.porcentaje_vip = None
                else:
                    rec.discapacidad = rec.partner_id.discapacidad
                    rec.complejidad = rec.partner_id.complejidad
                    rec.porcentaje_vip = rec.partner_id.porcentaje_vip

    def actualizar_mark_up(self):
        _logger.info("Entro en Action  Actualizar MU..............")
        for registro in self:
            _logger.info(registro.order_line)
            mu_servicio = registro.mu_servicio
            mu_equipo = registro.mu_equipo
            mu_insumo = registro.mu_insumo
            if registro.order_line:
                for rec in registro.order_line:
                    _logger.info("Muestro la linea :  .................")
                    _logger.info(rec)
                    _logger.info(rec._origin.product_template_id)
                    precio_unitario = rec._origin.product_template_id.list_price
                    if rec._origin.product_template_id and (rec._origin.product_template_id.hcd_categ_prod == 'servicio'):
                        if mu_servicio != 0:
                            _logger.info("Entro en  MarkUp servicio: .................")
                            _logger.info(mu_servicio)
                            porcentaje = (100 + mu_servicio)/100
                            _logger.info("Entro en  mu_servicio  Porcentaje : ..................")
                            _logger.info(porcentaje)

                            precio_unitario = round (rec._origin.costo_prestacion * porcentaje, 2)
                            _logger.info(precio_unitario)
                        
                    if rec._origin.product_template_id and (rec._origin.product_template_id.hcd_categ_prod == 'equipamiento'):
                        if mu_equipo != 0:
                            _logger.info("Entro en  MarkUp equipo: .................")
                            _logger.info(mu_equipo)
                            porcentaje = (100 + mu_equipo)/100
                            _logger.info("Entro en  mu_equipo  Porcentaje : ..................")
                            _logger.info(porcentaje)

                            precio_unitario = round (rec._origin.costo_prestacion * porcentaje, 2)
                            _logger.info(precio_unitario)
                        
                    if rec._origin.product_template_id and (rec._origin.product_template_id.hcd_categ_prod == 'material'):
                        if mu_insumo != 0:
                            _logger.info("Entro en  MarkUp insumo: .................")
                            _logger.info(mu_insumo)
                            porcentaje = (100 + mu_insumo)/100
                            _logger.info("Entro en  mu_insumo  Porcentaje : ..................")
                            _logger.info(porcentaje)

                            precio_unitario = round (rec._origin.costo_prestacion * porcentaje, 2)
                            _logger.info(precio_unitario)


                    _logger.info("Salio del if ....")
                    _logger.info(precio_unitario)
                    rec._origin.product_template_id.list_price = precio_unitario  # no se porque ... 
                    rec._origin.price_unit = rec.product_template_id.list_price
                    #rec.name = rec.product_template_id.description
        return
    
    
    def agregar_plan_trabajo_to_op(self):
        self.ensure_one()
        for registro in self:
            op_anteriores = self.env['hcd.plan_trabajo'].search(['&',('paciente_id','=',registro.partner_id.id),('status','=','activo')])
            if(len(op_anteriores) > 0) and registro.order_line :
                op_encontrada = False
                for order in registro.order_line:
                    fecha_inicio_order_line = order.start_date
                    _logger.info("Entrando en agregar Ppto a OP ...  muestro fecha inicio order line:...................")
                    _logger.info(fecha_inicio_order_line)
                    for op in op_anteriores:
                        if op.fecha_inicio <= fecha_inicio_order_line <= op.fecha_fin:
                            _logger.info("Se encontro una op que esta en rango de la orderline y se va a agregar a esta")
                            _logger.info(op.id)
                            _logger.info(op.name)
                            _logger.info("Lineas de servicios :..............")
                            _logger.info(id)
                            dic_line = {
                                'plan_id' : op.id,
                                'product_id' : order.product_id.product_tmpl_id.id,
                                'cantidad' : order.cantidad_prestacion,
                                'frecuencia': order.frecuencia,
                                'dias_ids': order.dias_ids,
                                'fechas_seleccionadas': order.fechas_seleccionadas,
                                'fecha_aux_ini': order.start_date,
                                'fecha_aux_fin': order.end_date,
                                'hora_inicio': 8,       #lo pongo por defecto , para que no vaya vacio  Salvo las guardias , es irrelevante
                                'cantidad_horas': 1,
                                'nro_autorizacion': order.nro_autorizacion,
                                'estado' :  'no_asignado'
                                }
                            _logger.info("Diccionario : ..................")
                            _logger.info(dic_line)
                            record_line_orig = self.env['hcd.plan_trabajo_line_original'].create(dic_line)  # lo grabo en Originales , para visualizar
                            record_line = self.env['hcd.plan_trabajo_line'].create(dic_line)
                            registro.write({'estado_pt': 'AGREGADO OP'})
                            op_encontrada = True
                            break
                if(not op_encontrada):
                    raise ValidationError('No se encontro una Orden de Prestación con el mismo rango de la prestación presupuestada')
        return #{   
        #     'type': 'ir.actions.client',
        #     'tag': 'reload'
        # }

    def create_plan_trabajo_from_sale(self):
        #fecha_hoy = datetime.now()
        for applicant in self:
            empleado_id=1  #revisar
            nombre_pt = 'algo_fallo'
            if applicant.partner_id and applicant.date_order:
                #nombre_pt = applicant.partner_id.name + '_' + applicant.date_order.strftime('%m/%Y')
                nombre_pt = applicant.partner_id.name + '_' + applicant.default_start_date.strftime('%d/%m/%Y') + '_' + applicant.default_end_date.strftime('%d/%m/%Y')
            if applicant.partner_id.coordinador_id :
                empleado_id = applicant.partner_id.coordinador_id.id
            _logger.info("Entro en Crea Plan..............")
            _logger.info(nombre_pt)
            dic = {
                'paciente_id' : applicant.partner_id.id,
                'fecha_inicio' : applicant.default_start_date,
                'fecha_fin' : applicant.default_end_date,
                #'fecha_creacion' : fecha_hoy,
                'fecha_creacion' : applicant.default_start_date,
                'empleado_id' : empleado_id,
                'name' : nombre_pt,
                'status' :  'activo'
            }
            record = self.env['hcd.plan_trabajo'].create(dic)
            
            if record:
                applicant.write({'estado_pt': 'CREADO'})

            plan_id = record.id
            pagador_id = applicant.filtro_id    
            # if ( applicant.paga_paciente == 'NO'):     #  tengo que ver quien paga , pero ya está en filtro_id
            #     pagador_id = applicant.
                
            # falta grabar las prestaciones  como prestaciones_originales para visualizar , no editables
            #     
            # grabo todas las prestaciones en hcd_plan_trabajo_line
            lista_ids = applicant.order_line
            for id in lista_ids:
                
                _logger.info("Lineas de servicios :..............")
                _logger.info(id)
                dic_line = {
                    'plan_id' : plan_id,
                    'product_id' : id.product_template_id.id,
                    'cantidad' : id.cantidad_prestacion,
                    'cantidad_total' : id.product_uom_qty,
                    'precio': id.price_unit,
                    'costo': id.costo_prestacion,
                    'frecuencia': id.frecuencia,
                    'dias_ids': id.dias_ids,
                    'fechas_seleccionadas': id.fechas_seleccionadas,
                    'fecha_aux_ini': id.start_date,
                    'fecha_aux_fin': id.end_date,
                    'hora_inicio': 8,       #lo pongo por defecto , para que no vaya vacio  Salvo las guardias , es irrelevante
                    'cantidad_horas': 1,
                    'pagador_id': pagador_id,
                    'nro_autorizacion': id.nro_autorizacion,
                    'estado' :  'no_asignado'
                    }
                _logger.info("Diccionario : ..................")
                _logger.info(dic_line)
                record_line_orig = self.env['hcd.plan_trabajo_line_original'].create(dic_line)  # lo grabo en Originales , para visualizar
                record_line = self.env['hcd.plan_trabajo_line'].create(dic_line)

                if id.product_template_id and id.product_template_id.hcd_categ_prod == 'modulado':
                    modulado_id = id.product_template_id.modulado_id.id
                    modulado = self.env['hcd.modulado'].search([('id','=', modulado_id)])
                    if(modulado):
                        _logger.info("Es modulado (encontrado)..............")
                        for id in modulado.producto_ids:     #lista de modulado_line
                                        
                            _logger.info("Lineas de servicios del MODULADO:..............")
                            _logger.info(id)
                            dic_line = {
                                'plan_id' : plan_id,
                                'product_id' : id.product_id.id,
                                'cantidad' : id.cantidad,
                                'cantidad_total' : id.cantidad_total,
                                'precio': id.precio,
                                'costo': id.costo,
                                'frecuencia': id.frecuencia,
                                'dias_ids': id.dias_ids,
                                'fechas_seleccionadas': id.fechas_seleccionadas,
                                'fecha_aux_ini': id.fecha_aux_ini,
                                'fecha_aux_fin': id.fecha_aux_ini,
                                'hora_inicio': 8,       #lo pongo por defecto , para que no vaya vacio  Salvo las guardias , es irrelevante
                                'cantidad_horas': 1,
                                # 'pagador_id': pagador_id,
                                # 'nro_autorizacion': id.nro_autorizacion,
                                'estado' :  'no_asignado'
                                }
                            _logger.info("Diccionario : ..................")
                            _logger.info(dic_line)
                            record_line_orig = self.env['hcd.plan_trabajo_line_original'].create(dic_line)  # lo grabo en Originales , para visualizar
                            record_line = self.env['hcd.plan_trabajo_line'].create(dic_line)


                # si es un servicio y es tipo guardia , genero agenda  -->  SE DEFINIO NO HACERLO DESDE ACA
                # if id.product_template_id.hcd_categ_prod == 'servicio':
                #     prefijo = id.product_template_id.nomenclador_id.categoria_id.prefijo
                #     if prefijo == 'BCGE' or prefijo == 'GCUI' or prefijo == 'GENF' or prefijo == 'GPED':
                #         _logger.info("Validado el codigo de nomenclador para crear agenda : .............")
                #         self.name = nombre_pt
                #         generar_agenda(self, id.start_date, id.end_date, plan_id, applicant.partner_id.id, applicant.partner_id.coordinador_id.id,record_line)
                #         _logger.info(prefijo)
                        
        return 