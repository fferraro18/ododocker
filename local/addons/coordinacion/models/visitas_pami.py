from pyexpat import model
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from functools import reduce
from odoo import fields, models


import logging
_logger = logging.getLogger(__name__)

def buscar_OP_Activa_paciente(self, nro_afiliado_pami):
    afiliado_con_barra = agregar_barra_nro_afiliado(nro_afiliado_pami)
    _logger.info("Se esta yendo a buscar un plan de trabajo con nro de afiliado: %s", afiliado_con_barra )
    planes_trabajo = self.env['hcd.plan_trabajo'].search(['&', ('paciente_id.nro_afiliado','like',afiliado_con_barra),'|',('status_pami','=','valida_con_visitas'),('status_pami','=','valida_sin_visitas') ])
    _logger.info(planes_trabajo)
    return planes_trabajo

def obtener_paciente_activo(nro_beneficio,self):
    paciente = self.env['res.partner'].search([('nro_afiliado','=',nro_beneficio),('hcd_type','=','paciente'), ('estado_paciente','=','activo')])
    return paciente

def obtener_planes_sin_visitas(self):
    planes_trabajo = self.env['hcd.plan_trabajo'].search([('status_pami','=','valida_sin_visitas')])
    _logger.debug("encontrados plan de trabajo sin fecha inicio")
    _logger.debug(planes_trabajo)
    return planes_trabajo
    

# def quitar_barra_nro_afiliado(nro_afiliado):
#     valores = nro_afiliado.strip().split('/')
#     return valores[0].strip() + valores[1].strip()

def quitar_barra_nro_afiliado(nro_afiliado):
    valores = nro_afiliado.strip()
    valores = valores.split('/')
    if (len(valores)>1):
        return valores[0].strip() + valores[1].strip()
    else: 
        return valores
    #return valores

def agregar_barra_nro_afiliado(nro_afiliado):
    return nro_afiliado[:-2] + ' / ' + nro_afiliado[-2:]
    

def esta_en_rango(fecha_visita, fecha_creacion, self):
    visita_date = datetime.strptime(fecha_visita, '%d/%m/%Y %H:%M:%S').date()
    delta = 3 + contar_no_laborables(fecha_creacion, visita_date, self)
    delta_ds = timedelta(days = delta)
    fecha_vencimiento = fecha_creacion + delta_ds
    return fecha_creacion <= visita_date <= fecha_vencimiento

def contar_dias_habiles(fecha_desde, fecha_hasta, self):
    all_days = contar_dias(fecha_desde, fecha_hasta)
    feriados = feriados_entre_fechas(fecha_desde, fecha_hasta, self)
    count = sum(1 for day in all_days if day.weekday() < 5)
    return count - len(feriados)

def contar_no_laborables(fecha_desde, fecha_hasta, self):
    all_days = contar_dias(fecha_desde, fecha_hasta)
    feriados = feriados_entre_fechas(fecha_desde, fecha_hasta, self)
    count = sum(1 for day in all_days if day.weekday() > 5)
    return count + len(feriados)

def contar_dias(fecha_desde, fecha_hasta):
    _logger.debug("Fecha desde es de tipo: %s", type(fecha_desde))
    _logger.debug("Fecha hasta es de tipo: %s", type(fecha_hasta))
    return (fecha_desde + timedelta(x + 1) for x in range((fecha_desde - fecha_hasta).days))

def feriados_entre_fechas(fecha_desde, fecha_hasta, self):
    feriados = self.env['hcd.feriados'].search([('feriado', '>=', fecha_desde),('feriado','<=',fecha_hasta)])
    _logger.debug("Feridos encontrados: %s", len(feriados))
    return feriados

def setear_fecha_fin(fecha_inicio, duracion):
    _logger.debug("La duracion de la op es: %s meses", duracion)
    
    delta_mes = relativedelta(months = duracion)
    delta_dias = timedelta(days=1)
    fecha_fin = fecha_inicio + delta_mes - delta_dias
    _logger.info("La fecha fin queda: %s", fecha_fin)
    return fecha_fin

# def is_paciente_activo(visita, self):
#     paciente = obtener_paciente(visita.nro_afiliado_pami, self)
#     return None

def filtrar_visitas_pacientes_existentes(visitas_seleccionadas, self):
    #modificar la lista para que haga una sola busqueda por paciente, tal vez usando un set y un filter
    lista_visitas_remanentes = []
    for visita in visitas_seleccionadas:
        paciente = obtener_paciente_activo(agregar_barra_nro_afiliado(visita.nro_afiliado_pami), self)
        if(not paciente):
            _logger.info("No se econtro el paciente con nro_afiliado: %s", visita.nro_afiliado_pami)
            visita.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'El paciente seleccionado no existe en nuestros registros con ese nro afiliado pami'})
        else:
            lista_visitas_remanentes.append(visita)
    return list(lista_visitas_remanentes)

def filtrar_visitas_op_inexistentes(visitas_seleccionadas, self):
    list_visitas = []
    for visita in visitas_seleccionadas:
        op_activa = buscar_OP_Activa_paciente(self, visita.nro_afiliado_pami)
        if(not op_activa):
            _logger.info("No se econtro una Op activa para el paciente con nro_afiliado: %s", visita.nro_afiliado_pami)
            visita.write({'estado_procesamiento': 'procesado_error', 'descripcion_error':'El paciente no esta relacionado a ninguna OP activa'})
        else:
            list_visitas.append(visita)
    return list(list_visitas)

def contabilizar_visitas(visitas_seleccionadas, self):
    _logger.info("Entro en contabilizar  .............")
    for visita_seleccionada in visitas_seleccionadas:
        _logger.info("Entro en contabilizar, adentro del for  .............")
        #en el siguiente if validar tambien si el paciente_seleccionado esta activo
        if visita_seleccionada.estado_procesamiento == 'sin_procesar':
            tipo_prestador_recuperado = visita_seleccionada.tipo_prestador  # por ejemplo 'Enfermera/o'
            tipo_prestador = tipo_prestador_recuperado[0]    # obtengo la primera letra , para buscar por categoria nomenclador
            _logger.info("Tipo de prestador  (letra): .............")
            _logger.info(tipo_prestador)
            op_activa_paciente = buscar_OP_Activa_paciente(self, visita_seleccionada.nro_afiliado_pami)
            #Si no encuetra el paciente marco el error de procesamiento
            for op in op_activa_paciente:   #porque recorro varias OP ?  no deberia haber una sola ? 
                _logger.info("Entro en contabilizar , OP activa: .............")
                lista_ids = op.producto_ids
                prestacion_encontrada = False
                for id in lista_ids:
                    if id.product_id.hcd_categ_prod == 'servicio':    #ahora la busqueda es por DNI ! 
                        tipo = id.product_id.nomenclador_id.categoria_id.tipo    #  E:  enfermero   C : cuidador  K : kinesio  etc 
                        _logger.info("Tipo de nomenclador (letra): .............")
                        _logger.info(tipo)
                        if tipo == tipo_prestador:
                            id.cantidad_realizadas += 1
                            _logger.info("Cantidad: .............")
                            _logger.info(id.cantidad_realizadas)
                            prestacion_encontrada = True
                if(not prestacion_encontrada):
                        _logger.info("no existe una prestacion asociada para los servicios")
                        #setear el error a la visita item C) de el doc de kate
            visita_seleccionada.estado_procesamiento = 'procesado'    
    #  relevar todos los errores posibles , cambiar el estado correspondiente 
    return 

def procesar_planes_validos_sin_visitas(visitas_seleccionadas, self):
    planes_validos_sin_visitas = obtener_planes_sin_visitas(self)
    # por cada plan de trabajo en estado teorico verifico si corresponde a una primera visita
    fechas_visitas_validas = []
    
    for plan in planes_validos_sin_visitas:
        for visita_seleccionada in visitas_seleccionadas:
            if not plan.fecha_inicio:
                nro_afiliado_del_plan = quitar_barra_nro_afiliado(plan.paciente_id.nro_afiliado)
                if visita_seleccionada.nro_afiliado_pami == nro_afiliado_del_plan:
                    fecha_visita = visita_seleccionada.fecha_comienzo
                    if (esta_en_rango(fecha_visita, plan.fecha_creacion, self)):
                        #si el plan de trabajo no tiene fecha de inicio me fijo si el paciente tiene una fecha de visita que esta dentro del rango de creacion del plan
                        _logger.debug("La fecha matchea como posible fecha de inicio: %s para el plan, nro: %s", fecha_visita, nro_afiliado_del_plan)
                        fechas_visitas_validas.append(fecha_visita)
        if len(fechas_visitas_validas) != 0:
            #obtener la menor fecha fechas_visitas_validas
            min_fecha_valida = reduce(lambda x, y:x if x < y else y, fechas_visitas_validas)
            plan.write({'fecha_inicio':datetime.strptime(min_fecha_valida, '%d/%m/%Y %H:%M:%S')})
            plan.write({'status_pami':'valida_con_visitas'})
            plan.write({'fecha_fin':setear_fecha_fin(plan.fecha_inicio, plan.duracion_op)})
            for plan_trabajo_line in plan.producto_ids:
                plan_trabajo_line.write({'fecha_aux_ini':datetime.strptime(min_fecha_valida, '%d/%m/%Y %H:%M:%S')})
                plan_trabajo_line.write({'fecha_aux_fin':setear_fecha_fin(plan_trabajo_line.fecha_aux_ini, plan_trabajo_line.duracion)})
            #agregar fecha de inicio y fin de los plan_trabajo_lines

class ModeloVisitasPami(models.Model):

    STATES = [
    ('sin_procesar', 'Sin Procesar'),
    ('procesado_error', 'Error'),
    ('procesado', 'Procesado'),
    ]

    _name = "hcd.visitas_pami"
    _description = "Modelo de importacion de Visitas de Pami"
    name = fields.Char("Nombre persona afiliada")
    nro_afiliado_pami = fields.Char("N° afiliación")
    nro_visita = fields.Char("N° de Visita")
    estado = fields.Char("Estado")
    fecha_comienzo = fields.Char("Fecha comienzo")
    fecha_fin = fields.Char("Fecha fin")
    duracion = fields.Char("Duración")
    celular_afiliado = fields.Char("Celular persona afiliada")
    dni_prestador = fields.Char("DNI del responsable de la visita")
    responsable = fields.Char("Responsable de la visita")
    matricula = fields.Char("N° matrícula responsable de la visita")
    tipo_prestador = fields.Char("Tipo servicio prestador")
    email_prestador = fields.Char("Email responsable de la visita")
    razon_social = fields.Char("Razón social de Empresa Prestadora")
    sap_empresa_prestadora = fields.Char("SAP de Empresa Prestadora")
    ugl_empresa_prestadora = fields.Char("UGL de Empresa Prestadora")
    
    estado_procesamiento = fields.Selection(STATES, default=STATES[0][0],help="Procesado del plan de trabajo")
    descripcion_error= fields.Char("Descripcion del error")

    _sql_constraints = [
        ('nro_visita_uniq', 'unique (nro_visita)', 'Esa visita ya fue subida!'),
    ]
    
    def procesar_visitas_pami(self):
        visitas_seleccionadas = self.browse(self._context.get('active_ids',[]))
        visitas_iniciales = len(visitas_seleccionadas)
        visitas_con_pacientes_existentes = filtrar_visitas_pacientes_existentes(visitas_seleccionadas, self)
        visitas_filtradas_paciente_prestacion_inexistente =  filtrar_visitas_op_inexistentes(visitas_con_pacientes_existentes, self) 
        procesar_planes_validos_sin_visitas(visitas_filtradas_paciente_prestacion_inexistente, self)
        _logger.info("Antes de contabilizar visita: ")
        _logger.info(len(visitas_filtradas_paciente_prestacion_inexistente))
        contabilizar_visitas(visitas_filtradas_paciente_prestacion_inexistente, self)
        visitas_fitradas = len(visitas_filtradas_paciente_prestacion_inexistente)

        mensaje = ''
        if(visitas_fitradas - visitas_iniciales == 0):
            mensaje = mensaje + 'ninguna visita pudo ser procesada'
        else:
            mensaje = str(visitas_fitradas) + ' visita/s fue/fueron procesada/s y ' + str(visitas_fitradas - visitas_iniciales) + ' contienen errores'

        return {
            'effect':{
                'fadeout':'slow',
                'message': mensaje,
                'type':'rainbow_man'
            }
        }