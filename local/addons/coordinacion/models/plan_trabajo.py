from ast import Str
from time import strftime
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
import logging
_logger = logging.getLogger(__name__)

DIARIA = 'diaria'  # todos los días
SEMANAL = 'semanal'
QUINCENAL = 'quincenal'
MENSUAL = 'mensual'
# cada 48 hs , todods los días desde fecha_inicio y con delta (days=2)
CADA48 = 'cada48'
# cada 72 hs , todods los días desde fecha_inicio y con delta (days=3)
CADA72 = 'cada72'
LUNVIER = 'lunesAviernes'
SABDOM = 'sabadoYdomingo'

DIAS_SEMANA = ['1', '2', '3', '4', '5']
SAB_DOM = ['6', '7']

# def generar_fecha_hora(fecha, hora_inicio):

#my_date = datetime.datetime(fecha.year, fecha.month, fecha.day, hora_inicio, 0, 0 ,0)
# tz_AR = pytz.timezone('America/Argentina/Buenos_Aires')
# fecha = tz_AR.localize(my_date)
# _logger.info("La fecha se genera como:")
# _logger.info(fecha.strftime("%m/%d/%Y, %H:%M:%S"))
# si se le setea el timeZone, al guardar el dato va a tirar un error naive porque
# la db esta sin timezone y se ve que no puede agregar el GMT-3 en el campo
# return my_date


def generar_fecha_hora(fecha, hora_inicio):
    #TIME_ZONE_AR = 3
    delta_hr = timedelta(hours=3)
    my_date = datetime(fecha.year, fecha.month,
                       fecha.day, hora_inicio, 0, 0, 0)
    my_date += delta_hr
    return my_date


def busca_excepcion_costo(self, prestador_id, paciente_id, nomenclador_id, fecha_actual):
    costo = 0

    excepciones = self.env['hcd.excepcion_costo_prestador'].search([
        ('prestador_id.id', '=', prestador_id), ('fecha_ini', '<=', fecha_actual), ('fecha_fin', '>=', fecha_actual), ])

    for excepcion in excepciones:
        # son cuatro combinaciones , 2 IF anidados
        _logger.info(
            "Entro en Excepcion con prestador ID  y nomenclador ID....................:")
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


def generar_agenda(self, fecha_inicio, fecha_fin, plan_id, paciente_id, empleado_id, product_line, estado):
    _logger.info("Entro con  la fecha  INICIAL:")
    _logger.info(fecha_inicio)
    frecuencia = product_line.frecuencia
    name = self.name
    delta = timedelta(days=1)
    if frecuencia == CADA48:
        delta = timedelta(days=2)
    if frecuencia == CADA72:
        delta = timedelta(days=3)
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        # si la fecha es un feriado no tenerla en cuenta.
        # implementar esta logica
        # if is_feriado(fecha_actual):
        #     fecha_actual += delta
        #     continue
        agregarRegistro = False
        if (frecuencia == DIARIA) | (frecuencia == CADA48) | (frecuencia == CADA72):
            agregarRegistro = True
        elif frecuencia == SEMANAL:
            agregarRegistro = cumple_condicion_semanal_obj(
                fecha_actual, product_line.dias_ids)
        elif frecuencia == LUNVIER:
            agregarRegistro = cumple_condicion_semanal(
                fecha_actual, DIAS_SEMANA)
        elif frecuencia == SABDOM:
            agregarRegistro = cumple_condicion_semanal(fecha_actual, SAB_DOM)
        elif (frecuencia == QUINCENAL) | (frecuencia == MENSUAL):
            agregarRegistro = cumple_condicion_quincenal(
                fecha_actual, product_line.fechas_seleccionadas)

        if(agregarRegistro):
            costo_excepcion = 0
            precio_prestacion = product_line.precio
            prestador_id = None
            proveedor_id = None
            nomenclador_id = None

            if product_line.proveedor_id:
                proveedor_id = product_line.proveedor_id.id
            if product_line.prestador_id:
                prestador_id = product_line.prestador_id.id
                if product_line.product_id and product_line.product_id.nomenclador_id:
                    nomenclador_id = product_line.product_id.nomenclador_id.id
                    costo_excepcion = busca_excepcion_costo(
                        self, prestador_id, paciente_id, nomenclador_id, fecha_actual)

            if (costo_excepcion == 0):
                _logger.info("--------------------  el costo es :")
                _logger.info(product_line.costo)
                costo_excepcion = product_line.costo
            fecha_hora = generar_fecha_hora(
                fecha_actual, product_line.hora_inicio)
            dic_linea = {
                'name': name,
                'plan_trabajo_id': plan_id,
                'paciente_id': paciente_id,
                'prestador_id': prestador_id,
                'proveedor_id': proveedor_id,
                'empleado_id': empleado_id,
                'plan_trabajo_line_id': product_line.id,
                'fecha_visita': fecha_hora,
                'duracion': product_line.cantidad,
                'producto_id': product_line.product_id.id,
                'nro_autorizacion': product_line.nro_autorizacion,
                'costo_prestacion': costo_excepcion,
                'precio_prestacion': precio_prestacion,
                'estado': estado,
                'observaciones': product_line.observaciones
            }

            _logger.info("Se va a guardar la agenda con la fecha:")
            _logger.info(fecha_hora.strftime("%m/%d/%Y, %H:%M:%S"))
            agregar_registro_agenda(self, dic_linea)
        fecha_actual += delta


def cumple_condicion_semanal(fecha, condicion):
    _logger.info("cumple condicion Semanal")
    for dia_selecionado in condicion:
        #_logger.info("dia seleccionado" )
        # _logger.info(dia_selecionado)
        #_logger.info( "dia actual" + str(fecha.isoweekday()))
        if (str(fecha.isoweekday()) == dia_selecionado):
            return True
    return False


def cumple_condicion_semanal_obj(fecha, condicion):
    _logger.info("cumple condicion Semanal    OBJ")
    for dia_selecionado in condicion:
        #_logger.info("dia seleccionado:............." )
        # _logger.info(dia_selecionado.id)
        #_logger.info( "dia actual" + str(fecha.isoweekday()))
        if (fecha.isoweekday() == dia_selecionado.id):
            return True
    return False


def cumple_condicion_quincenal(fecha, condicion):
    for dia_condicion in condicion.split(","):
        dia_seleccionado = datetime.strptime(dia_condicion, '%d/%m/%Y')
        if fecha == dia_seleccionado.date():
            #_logger.info("Fecha encontrada" + str(fecha))
            return True
    #_logger.info("Fecha no encontrada")
    return False


def agregar_registro_agenda(self, dic_linea):
    record_linea = self.env['hcd.agenda'].create(dic_linea)


def validar_campos(product_line):
    frecuencia = product_line.frecuencia
    if (not product_line.fecha_aux_ini) or (not product_line.fecha_aux_ini):
        raise ValidationError(
            _("la fecha de inicio y fin tienen que estar definidas"))
    if (product_line.cantidad <= 0):
        raise ValidationError(
            _("la cantidad de horas no puede se cero o negativa"))
    if(not frecuencia):
        raise ValidationError(_("Por favor seleccione una frecuencia valida"))
    # if( not product_line.prestador_id):
    #    raise ValidationError(_("Por favor seleccione un prestador"))
    if(frecuencia == SEMANAL and not product_line.dias_ids):
        raise ValidationError(
            _("Debe seleccionar al menos un dia para la frecuencia semanal"))
    if((frecuencia == QUINCENAL or frecuencia == MENSUAL) and not product_line.fechas_seleccionadas):
        raise ValidationError(
            _("Debe seleccionar una fecha para la frecuencia seleccionada"))


class PlanTrabajo(models.Model):
    _inherit = ["mail.thread"]
    _name = 'hcd.plan_trabajo'

    STATES = [
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('asignado', 'Asignado'),
        ('agendado', 'Agendado'),
        ('prorrogado', 'Prorrogado'),
        ('finalizado', 'Finalizado'),
    ]

    STATES_PAMI = [
        ('no_pami', 'NO es PAMI'),
        ('valida_sin_visitas', 'Válida sin visitas'),
        ('valida_con_visitas', 'Válida con visitas'),
        ('valida_no_req__visitas', 'Válida no req. visitas'),
        ('valida_internacion', 'Válida Internación'),
        ('valida_baja', 'Válida BAJA'),
        ('valida_obito', 'Válida OBITO'),
        ('invalida_sin_visitas', 'Inválida sin visitas'),
        ('invalida_30d', 'Inválida Int +30d'),
        ('invalida_72h', 'Inválida + 72hs'),
        ('vencida', 'Vencida'),
    ]

    name = fields.Char(required=True)
    descripcion = fields.Char("Descripción")
    comment = fields.Char("Comentarios")
    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        domain="['|',('hcd_type', '=', 'paciente'),('hcd_type', '=', 'cliente_paciente')]",
        help='Paciente asociado al plan de trabajo'
    )

    empleado_id = fields.Many2one(
        'hr.employee', 'Coordinador',
        help='Coordinador'
    )

    # coordinador_id_view = fields.Char(compute="_get_coordinador_id")
    fecha_inicio = fields.Date('Fecha de Inicio')
    fecha_fin = fields.Date('Fecha de Fin')
    fecha_creacion = fields.Date('Fecha de Activada')
    duracion_op = fields.Integer("duracion de la OP", default=1)

    status = fields.Selection(
        STATES, default=STATES[0][0], help="Estado del plan de trabajo")

    status_pami = fields.Selection(
        STATES_PAMI, default=STATES_PAMI[0][0], readonly=True, string='Estado Pami', help="Estado de la OP de Pami")

    producto_ids = fields.One2many(
        'hcd.plan_trabajo_line', 'plan_id', string='Servicios')

    producto_ids_original = fields.One2many(
        'hcd.plan_trabajo_line_original', 'plan_id', string='Prestaciones originales')

    # necesario para el chatter
    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', string='Followers', groups='base.group_user')

    activity_ids = fields.One2many(
        'mail.activity', 'calendar_event_id', string='Activities')
    message_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        domain=lambda self: [('message_type', '!=', 'user_notification')], auto_join=True)

    obra_social_view = fields.Char(compute="_get_obra_social_pt")
    nodo_view = fields.Char(compute="_get_nodo_pt")
    # para filtrar los servicios
    filtro_id = fields.Integer(compute="_get_filtro_id")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre ya existe!'),
    ]

    def _get_obra_social_pt(self):
        for rec in self:
            if rec.paciente_id and (rec.paciente_id.obra_social_id != None):
                rec.obra_social_view = rec.paciente_id.obra_social_id.name
            else:
                rec.obra_social_view = ''

    def _get_nodo_pt(self):
        for rec in self:
            if rec.paciente_id and (rec.paciente_id.nodo_id != None):
                rec.nodo_view = rec.paciente_id.nodo_id.name
            else:
                rec.nodo_view = 'Indefinido'

    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_two_date_pt(self):
        for record in self:
            if (record.fecha_inicio) and (record.fecha_fin):
                start_date = record.fecha_inicio.strftime('%Y-%m-%d')
                end_date = record.fecha_fin.strftime('%Y-%m-%d')
                if start_date > end_date:
                    raise ValidationError(
                        "La fecha de inicio no puede ser mayor a la fecha fin")

    @api.onchange('paciente_id')
    def _get_filtro_id(self):
        for rec in self:
            rec.filtro_id = 0
            if rec.paciente_id:
                # or (rec.paga_paciente == 'SI'):
                if (rec.paciente_id.hcd_type == 'cliente'):
                    rec.filtro_id = rec.paciente_id.id

                elif (rec.paciente_id.obra_social_id):
                    rec.filtro_id = rec.paciente_id.obra_social_id.id

    # @api.onchange('paciente_id')
    # def _get_coordinador_id(self):
    #     for rec in self:
    #         rec.coordinador_id_view = 0
    #         if rec.paciente_id and (rec.paciente_id.coordinador_id != None):
    #             rec.coordinador_id_view = rec.paciente_id.coordinador_id

    def crea_agenda(self):
        for applicant in self:
            plan_id = applicant.id

            paciente_id = applicant.paciente_id.id
            empleado_id = applicant.empleado_id.id
            lista_ids = applicant.producto_ids
            for product_line in lista_ids:
                # if  product_line.product_id and product_line.product_id.hcd_categ_prod and (product_line.product_id.hcd_categ_prod == 'servicio') and (product_line.estado == 'no_asignado'):
                #     fecha_inicio = applicant.fecha_inicio
                #     fecha_fin = applicant.fecha_fin
                #     prefijo = product_line.product_id.nomenclador_id.categoria_id.prefijo
                if (product_line.fecha_aux_ini):
                    fecha_inicio = product_line.fecha_aux_ini
                if (product_line.fecha_aux_fin):
                    fecha_fin = product_line.fecha_aux_fin

                validar_campos(product_line)
                creo_agenda = False
                estado = 'indefinido'
                if (product_line.estado == 'no_asignado' or product_line.estado == 'primer_visita'):
                    if (product_line.product_id.hcd_categ_prod == 'servicio'):
                        if product_line.prestador_id:  # si tiene prestador asignado, creo_agenda
                            creo_agenda = True
                            estado = 'asignado'
                        else:
                            #prefijo = product_line.product_id.nomenclador_id.categoria_id.prefijo
                            # if prefijo == 'BCGE' or prefijo == 'GCUI' or prefijo == 'GENF' or prefijo == 'GPED':
                            # no asignado,sin prestador , pero es guardia, lo creo en agenda  estado Agendado
                            creo_agenda = True
                            estado = 'agendado'
                    else:  # no es servicio
                        creo_agenda = True
                        estado = 'agendado'

                if creo_agenda:
                    generar_agenda(self, fecha_inicio, fecha_fin, plan_id,
                                   paciente_id, empleado_id, product_line, estado)
                    product_line.write({'estado': estado})
                    _logger.debug("Saliendo de Grabar Agenda ...............")

        return {
            'name': _('Agenda'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
            'res_model': 'hcd.agenda',
            'domain': [('paciente_id', '=', paciente_id)]
        }

    def agenda_filtrada(self):
        for applicant in self:
            plan_id = applicant.id

            paciente_id = applicant.paciente_id.id
            return {
                'name': _('Plan de trabajo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,calendar',
                'res_model': 'hcd.agenda',
                'domain': [('paciente_id', '=', paciente_id)]
            }

    def primer_visita_pami(self):
        for applicant in self:
            plan_id = applicant.id
            empleado_id = None
            paciente_id = applicant.paciente_id.id
            if applicant.empleado_id:
                empleado_id = applicant.empleado_id.id
            lista_ids = applicant.producto_ids
            fecha = datetime.now()
            fecha_hora = generar_fecha_hora(fecha, 8)
            for product_line in lista_ids:
                # if  product_line.product_id and product_line.product_id.hcd_categ_prod and (product_line.product_id.hcd_categ_prod == 'servicio') and (product_line.estado == 'no_asignado'):
                #     fecha_inicio = applicant.fecha_inicio
                #     fecha_fin = applicant.fecha_fin
                #     prefijo = product_line.product_id.nomenclador_id.categoria_id.prefijo
                # if (product_line.fecha_aux_ini):
                #     fecha_inicio = product_line.fecha_aux_ini
                # if (product_line.fecha_aux_fin):
                #     fecha_fin = product_line.fecha_aux_fin
                fecha = datetime.now()

                if (product_line.estado == 'no_asignado'):
                    if (product_line.product_id.hcd_categ_prod == 'servicio'):
                        if product_line.prestador_id:  # si tiene prestador asignado, creo_agenda
                            creo_agenda = True
                            estado = 'primer_visita'
                            dic_linea = {
                                'name': applicant.name,
                                'plan_trabajo_id': plan_id,
                                'paciente_id': paciente_id,
                                'prestador_id': product_line.prestador_id.id,
                                'empleado_id': empleado_id,
                                'plan_trabajo_line_id': product_line.id,
                                'fecha_visita': fecha_hora,
                                'duracion': '1',
                                'producto_id': product_line.product_id.id,
                                'nro_autorizacion': product_line.nro_autorizacion,
                                'costo_prestacion': 0,
                                'precio_prestacion': 0,
                                'estado': estado,
                                'observaciones': 'Primer visita'
                            }
                            record_linea = self.env['hcd.agenda'].create(
                                dic_linea)
                            if record_linea:
                                product_line.write({'estado': estado})
                                _logger.debug(
                                    "Saliendo de Grabar Agenda ...............")

        return {
            'name': _('Agenda'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
            'res_model': 'hcd.agenda',
            'domain': [('paciente_id', '=', paciente_id)]
        }

    def notify_cron(self):
        _logger.info(f'Ejecutando CRON: {self}')
        try:
            #fecha = date_utils.add(obj_date, days=2)
            ord_tr = self.env['hcd.plan_trabajo'].search(
                [('status_pami', '=', 'valida_sin_visitas')])
            _logger.info(f'Ordenes a notificar: {ord_tr}')
        except Exception as e:
            _logger.info(f'Ocurrio una Exception: {e}')
        pass
