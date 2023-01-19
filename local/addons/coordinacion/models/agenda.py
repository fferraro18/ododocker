
from odoo import api,fields, models, _
import logging
_logger = logging.getLogger(__name__)

class Agenda(models.Model):
    _name = 'hcd.agenda'
    _table = 'agenda'

    name = fields.Char()
    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        domain="[('hcd_type', '=', 'paciente')]",
        help='Paciente asociado al plan de trabajo'
    )

    prestador_id = fields.Many2one(
        'res.partner', 'Prestador',
        domain="[('hcd_type', '=', 'prestador')]",
        help='Prestador asignado'
    )

    proveedor_id = fields.Many2one(
        'res.partner', 'Proveedor',
        domain="[('hcd_type', '=', 'proveedor'),('status', '=', 'activo')]",
        help='Proveedor asignado'
    )
    
    fecha_visita = fields.Datetime('Fecha de visita')
    duracion = fields.Float(string="Duración")
    
    plan_trabajo_line_id = fields.Many2one(
        'hcd.plan_trabajo_line', string='Servicio en orden de prestación',
    )

    plan_trabajo_id = fields.Many2one(
        'hcd.plan_trabajo', string='Orden de prestación',
    )

    empleado_id = fields.Many2one(
        'hr.employee', 'Empleado',
        help='Empleado encargado del plan'
    )
    prestador_id_view = fields.Char(compute="_get_prestador_id_agenda")
    obra_social_view = fields.Char(compute="_get_obra_social_agenda")
    descripcion_view = fields.Html(compute="_get_descripcion_producto_agenda")

    producto_id = fields.Many2one(
        'product.template', string='Servicio'
    )

    # obra_social_id = fields.Many2one(
    #     'res.partner', 'Cliente',
    #     domain="[('hcd_type', '=', 'cliente')]",
    #     tracking=True,
    #     help='Financiador actual del paciente'
    # )

    costo_prestacion = fields.Float("Costo")
    precio_prestacion = fields.Float("Precio")
    executed = fields.Datetime('Visita realizada')
    
    # ejecutado = fields.Many2one('agenda',string='Ejecutado',
        
    # domain="[('hcd_agenda.id', '=', 'agenda.id')]"
    #  )

    # agenda_app_id = fields.Many2one('agenda', compute='compute_stage', inverse='stage_inverse')
    # agenda_ids = fields.One2many('agenda', 'agenda_id')

    # id_agenda = fields.Integer('id de la agenda', related='agenda.id')

    # @api.depends('agenda_ids')
    # def compute_stage(self):
    #     if len(self.agenda_ids) > 0:
    #         self.agenda_app_id = self.agenda_ids[0]

    # def stage_inverse(self):
    #     if len(self.agenda_ids) > 0:
    #         # delete previous reference
    #         stage = self.env['agenda'].browse(self.agenda_ids[0].id)
    #         stage.agenda_app_id = False
    #     # set new reference
    #     self.agenda_app_id.stage_id = self











    estado = fields.Selection([
        ('primer_visita', '1er VISITA'),
        ('asignado', 'ASIGNADO'),
        ('no_asignado', 'NO ASIGNADO'),
        ('agendado', 'AGENDADO'),
        ('ejecutado', 'EJECUTADO'),
        ('internado', 'INTERNADO'),
        ('liquidado', 'LIQUIDADO'),
        ('facturado', 'FACTURADO'),
        ('pagado', 'PAGADO'),
        ('otro', 'OTRO'),
        ],
        help="Estado de la visita agendada") 

    estado_liq = fields.Selection([
        ('sin_procesar', 'SIN PROCESAR'),
        ('procesado', 'PROCESADO'),
        ('procesado_error', 'ERROR'),
        ],
        help="Estado de liquidación de visita agendada") 

    estado_fac = fields.Selection([
        ('sin_procesar', 'SIN PROCESAR'),
        ('procesado', 'PROCESADO'),
        ('procesado_error', 'ERROR'),
        ],
        help="Estado de facturación de visita agendada")
#agregar fecha de ejecucion , de liquidacion , de faturacion y de pago   (tabla aparte ???)

#agregados para liquidacion/facturacion

    confirmado = fields.Boolean()  #Identifica cuales son las líneas que deben ser prorrogables y actualiza precios y costos de los maestros
    fecha_confirmado = fields.Date()
    fecha_liquidado = fields.Date()
    fecha_facturado = fields.Date()
    fecha_pagado = fields.Date()
    no_prorrogar = fields.Boolean()
    copago = fields.Float()
    porcentaje_fc = fields.Integer()
    cant_ingreso = fields.Integer()
    cant_costo = fields.Integer()
    observaciones = fields.Char()
    nro_autorizacion = fields.Char("Nro. Autorización")

    @api.depends('prestador_id')
    def _get_prestador_id_agenda(self):
        for rec in self:
            rec.prestador_id_view = 0
            if rec.prestador_id and (rec.prestador_id.id != None):
                rec.prestador_id_view = rec.prestador_id.id

    @api.depends('paciente_id')
    def _get_obra_social_agenda(self):
        for rec in self:
            rec.obra_social_view = ''
            if rec.paciente_id and (rec.paciente_id.obra_social_id != None):
                rec.obra_social_view = rec.paciente_id.obra_social_id.name

    @api.depends('producto_id')
    def _get_descripcion_producto_agenda(self):
        for rec in self:
            if rec.producto_id:
                rec.descripcion_view = rec.producto_id.description
            else:
                rec.descripcion_view = ''