from odoo import fields, models
from datetime import datetime
import re
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
#from prestacion_pami import PrestacionPami
_logger = logging.getLogger(__name__)

def obtener_paciente(nro_beneficio,self):
    paciente = self.env['res.partner'].search([('nro_afiliado','=',nro_beneficio),('hcd_type','=','paciente')])
    return paciente

def buscar_ops_anteriores(paciente, modelo, self):
    return self.env['hcd.plan_trabajo'].search(['&',('paciente_id','=',paciente.id),'|',('status_pami','=','valida_sin_visitas'),('status_pami','=','valida_con_visitas')])
#chequear si encontro las op anteriores


def tiene_modulo_principal(modelo, self):
    modulados_id = getModulados_id(modelo.ep_aprobada)
    for modulado_id in modulados_id:
        modulado = self.env['hcd.modulado'].search([('codigo_cliente','=',modulado_id)])
        if(len(modulado)>1):
            _logger.info("ERROR   Encontro mas de un modulado con el codigo de cliente :------")
            modelo.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'Se encontró más de un módulo con ese código'})
            return False
            #Procesar error !!!!
        codigo_modulado_pami = int(modulado.codigo_cliente)
        _logger.info("Codigo modulado pami :------")
        _logger.info(codigo_modulado_pami)
        if(codigo_modulado_pami < 215000 or 
            codigo_modulado_pami == 227001 or 
            codigo_modulado_pami == 227002 or
            codigo_modulado_pami == 223006 or
            codigo_modulado_pami == 223007 or
            codigo_modulado_pami == 223008 ):
            return True
    return False

# Devuelve un diccionario en el que la key es el producto o prestacion y el valor la duracion de esa prestacion en base al modulo
def getModuladoLine(modelo, prestaciones, self):
    modulados_id = getModulados_id(modelo.ep_aprobada)
    resultado = {}
    for modulado_id in modulados_id:
        modulado = self.env['hcd.modulado'].search([('codigo_cliente','=',modulado_id)])
        if not modulado:
            _logger.info("no se encontro el modulado con el nro")
            modelo.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'no se pudo encontrar un modulado con el codigo de cliente'})
            return
        for producto_id in modulado.producto_ids:
            _logger.info("Prestaciones")
            _logger.info(prestaciones)
            _logger.info("Codigo de cliente")
            _logger.info(modulado.codigo_cliente)
            duracion_modulo = prestaciones.get(modulado.codigo_cliente)
            _logger.info("Se obtuvo una duracion para el modulo de %s", duracion_modulo)
            #TODO ver si se puede agregar al product_id la duracion como un atributo mas
            resultado[producto_id] = duracion_modulo
    return resultado

def get_duracion_prestacion(descripcion_op):
    duracionX = re.search(r"\(X\s\d\)", descripcion_op)
    if duracionX:
        valor_duracion = re.search(r"\d", duracionX.group())
        _logger.info("Se encontro una OP con duracion: %s", valor_duracion.group())
        return valor_duracion.group()
    else:
        _logger.info("No se encontro una duracion para la OP")
        return '0'

def get_descripcion_prestacion(descripcion_op):
    return re.sub('\([^)]*\)', '', descripcion_op).strip()

#  toma las prestaciones aprobadas como un string, en donde figura el id del modulo, la descripcion y la duracion
#  para devolver un diccionario con la id y la duracion de cada prestacio
# 213001 - MODULO MENSUAL REHABILITACION (X 3) -- 215001 - SUBMODULO MENSUAL DE EQUIPAMIENTO - CAMA ORTOPEDICA (X 3) -- 215002 - SUBMODULO MENSUAL DE EQUIPAMIENTO - COLCHON ANTIESCARA (X 3) --
def obtener_prestaciones(ep_aprobada):
    modulos_sub_modulos = ep_aprobada.strip().split('--')
    resultado = {}
    for modulo_sub_modulo in modulos_sub_modulos:
        if modulo_sub_modulo is not None:
            id_descripcion = modulo_sub_modulo.strip().split('-')
            if id_descripcion is not None and id_descripcion != '':
                # _logger.info("el estado descripcion contiene:")
                # _logger.info(id_descripcion)
                # 213001 - MODULO MENSUAL REHABILITACION (X 3)
                if(len(id_descripcion)>1):
                    descripcion_op = id_descripcion[1]
                    if(len(id_descripcion)>2):
                        descripcion_op += id_descripcion[2]
                    if descripcion_op is not None and descripcion_op != '':
                        _logger.info("id prestacion: %s ", id_descripcion[0].strip())
                        _logger.info("descripcion: %s ", get_descripcion_prestacion(descripcion_op))
                        _logger.info("duracion: %s ", get_duracion_prestacion(descripcion_op))
                        resultado[id_descripcion[0].strip()] = get_duracion_prestacion(descripcion_op)
    
    return resultado

def getDuracionOP(ep_aprobada):
    prestaciones = obtener_prestaciones(ep_aprobada)
    _logger.info("las prestaciones id:duracion son :")
    _logger.info(prestaciones)
    _logger.info(type(prestaciones))
    return max(prestaciones.values())

def calcular_duracion_prestacion(id, ep_aprobada):
    prestaciones = obtener_prestaciones(ep_aprobada)
    for key in prestaciones:
        if(key == id):
            return prestaciones[key]
    return 1

def getModulados_id(ep_aprobada):
    estados = ep_aprobada.strip().split('--')
    resultado = []
    for estado in estados:
        if estado is not None:
            estado_id_descripcion = estado.strip().split('-')
            if estado_id_descripcion is not None and estado_id_descripcion != '':
                id_estado = estado_id_descripcion[0]
                if id_estado is not None and id_estado != '':
                    resultado.append(id_estado.strip())
    return resultado

def  crear_plan_trabajo(nro_op, id, duracion_total_op, self):
    dic = {
        'name' : nro_op,
        'paciente_id' : id,
        'status' : 'borrador',
        'status_pami' : 'valida_sin_visitas',
        'fecha_creacion' : datetime.now(),
        'duracion_op': duracion_total_op
    }
    return self.env['hcd.plan_trabajo'].create(dic)

#crea el plan de trabajo_line, para eso usa un diccionario en donde la clave es el producto, o prestacion sacada del modulo y el valor es la duracion
def crear_plan_trabajos_line(modelo, id, modulados_line, self):
    _logger.info("las keys son el modulado")
    _logger.info(modulados_line)
    for plan_trabajo_line in modulados_line:
        _logger.info("Duracion de la prestacion para el id %s:", plan_trabajo_line)
        _logger.info(modulados_line[plan_trabajo_line])
        dic_line = crear_diccionario(modelo.nro_op, id,modulados_line[plan_trabajo_line], plan_trabajo_line)
        self.env['hcd.plan_trabajo_line'].create(dic_line)

def crear_plan_trabajos_line_con_fechas(modelo, id, modulados_line, self):
    for plan_trabajo_line in modulados_line:
        dic_line = crear_diccionario(modelo.nro_op, id, modulados_line[plan_trabajo_line], plan_trabajo_line)
        fecha_inicio = datetime.now()
        duracion = int(modulados_line[plan_trabajo_line])
        dic_line['fecha_aux_ini'] = fecha_inicio
        dic_line['fecha_aux_fin'] = setear_fecha_fin(fecha_inicio, duracion)
        self.env['hcd.plan_trabajo_line'].create(dic_line)

def crear_diccionario(nro_op, id, duracion, plan_trabajo_line):
    return {
            'plan_id' : id,
            'product_id' : plan_trabajo_line.product_id.id,
            'frecuencia' : plan_trabajo_line.frecuencia,
            'cantidad' : plan_trabajo_line.cantidad,
            'cantidad_total' : plan_trabajo_line.cant_max_mensual,
            'precio' : plan_trabajo_line.product_id.list_price,
            'costo' : plan_trabajo_line.product_id.costo,
            'estado' :  'no_asignado',
            'nro_op_pami': nro_op,
            'duracion' : duracion
            }

def setear_fecha_fin(fecha_inicio, duracion):
    _logger.debug("Se va a setear la fecha la fecha de fin para la situacion 2 %s", duracion)
    
    delta_mes = relativedelta(months = duracion)
    delta_dias = timedelta(days=1)
    fecha_fin = fecha_inicio + delta_mes - delta_dias
    _logger.info("La fecha fin queda: %s", fecha_fin)
    return fecha_fin

class ModeloPami(models.Model):

    STATES = [
    ('sin_procesar', 'Sin Procesar'),
    ('procesado_error', 'Error'),
    ('procesado', 'Procesado'),
    ]

    _name = "hcd.modelo_pami"
    _description = "Modelo de importacion de Pami"
    name = fields.Char("apellido y nombre")
    ugl = fields.Char("ugl")
    agencia = fields.Char("agencia")
    nro_op = fields.Char("nro. op")
    motivo_emision = fields.Char("motivo de emision")
    prestador_rechazo = fields.Char("prestador de rechazo")
    prestador = fields.Char("prestador")
    f_solicitud = fields.Char("f. Solicitud")
    nro_beneficio = fields.Char("nro. Beneficio/GP")
    solicitante = fields.Char("solicitante")
    estado = fields.Char("estado")
    ep_aprobada = fields.Char("estado de practica:aprobada")
    ep_rechazada = fields.Char("estado de practica:rechazada")
    ep_info_add = fields.Char("estado de practica:se solicita informacion adicional")
    ep_asig_turno = fields.Char("estado de practica:asignar turno")
    ep_conformar = fields.Char("estado de practica:conformar")
    ep_no_conformar = fields.Char("estado de practica:no conformar")
    pendiente_autorizacion = fields.Char("pendiente autorizacion")
    usuario_emisor = fields.Char("usuario emisor")
    estado_procesamiento = fields.Selection(STATES, default=STATES[0][0],help="Procesado del plan de trabajo")
    descripcion_error= fields.Char("Descripcion del error")


    _sql_constraints = [
        ('nro_op_uniq', 'unique (nro_op)', 'Esa OP ya fue subida!'),
    ]

    def generar_plan_trabajo(self):
        modelo_pami = self.browse(self._context.get('active_ids',[]))
        cant_planes = len(modelo_pami)
        cant_no_procesados = 0
        for modelo in modelo_pami:
            paciente = obtener_paciente(modelo.nro_beneficio, self)

            # si no existe el paciente salto pero debo marcar en el modulado pami procesado_con error
            if not paciente:
                _logger.debug("no se encontro el paciente con nro_beneficiario %s", modelo.nro_beneficio)
                modelo.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'No se encontro el paciente por el nro. de beneficiario'})
                cant_no_procesados += 1
                continue 
    #situaciones:
            op_anteriores = buscar_ops_anteriores(paciente,modelo, self)
    #situacion 1. 
            # No existe una op anterior 
            if(len(op_anteriores) == 0):
                # y este modelo tiene un modulo principal => <215000
                if(tiene_modulo_principal(modelo,self)):
                    prestaciones = obtener_prestaciones(modelo.ep_aprobada)
                    modulados_line = getModuladoLine(modelo,prestaciones, self)
                    if not modulados_line:
                        cant_no_procesados += 1
                        continue 
                    duracion_total_op =  max(prestaciones.values())
                    plan_trabajo = crear_plan_trabajo(modelo.nro_op, paciente.id, duracion_total_op, self)
                    crear_plan_trabajos_line(modelo, plan_trabajo.id, modulados_line, self)
                    modelo.estado_procesamiento='procesado'
                else:
                    _logger.debug("El modulo NO tiene una op anterior (es nueva) pero no tiene un modulo Principal.")
                    modelo.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'El modulo NO tiene una op anterior (es nueva) pero no tiene un modulo Principal.'})
    # #situacion 2. 
    #         # existe OP anterior, deberia haber una sola en teoria
            if(len(op_anteriores) != 0):
                # y el modelo tiene solo sub modulos
                if(not tiene_modulo_principal(modelo, self)):
                    # modifico la OP existente
                    prestaciones = obtener_prestaciones(modelo.ep_aprobada)
                    modulados_line = getModuladoLine(modelo,prestaciones, self)
                    if not modulados_line:
                        cant_no_procesados += 1
                        continue 
                    crear_plan_trabajos_line_con_fechas(modelo, op_anteriores[0].id, modulados_line, self)
                    modelo.estado_procesamiento='procesado'
                else:
                    _logger.debug("El modulo TIENE una op ,pero tiene un modulo Principal. Situacion 3 ")
                    #continuar con logica de situacion 3
                    modelo.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'El modulo Tiene una op anterior pero no tiene un modulo Principal.'})
                

        mensaje = ''
        if(cant_planes == 0):
            mensaje = mensaje + 'ningun registro pudo ser procesado'
        
        mensaje = str(cant_planes) + ' registro/s fue/fueron procesado/s y ' + str(cant_no_procesados) + ' contienen errores'
        return {
            'effect':{
                'fadeout':'slow',
                'message': mensaje,
                'type':'rainbow_man'
            }
        }