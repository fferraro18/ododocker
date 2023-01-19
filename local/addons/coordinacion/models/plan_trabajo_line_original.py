from odoo import api,fields, models, _
import logging
_logger = logging.getLogger(__name__)

class PlanTrabajoLineOriginal(models.Model):
    _name = "hcd.plan_trabajo_line_original"
    _description = "Plan de Trabajo Line Original"
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
   
    cantidad_horas = fields.Integer()
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

    hora_inicio = fields.Integer() # agregar validacion <24
    nro_autorizacion = fields.Char("Nro. Autorización")
    estado = fields.Selection([
         ('asignado', 'Asignado'),
         ('no_asignado', 'No asignado'),
         ('indefinido', 'indefinido'),
         ('modificado', 'Modificado'),
         ('rechazado', 'Rechazado'),],
         default='no_asignado',)
         
    #No se usan !

    # prestador_id = fields.Many2one(
    #     'res.partner', 'Efector',
    #     domain="['|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector'),('status', '=', 'activo')]",
    #     help='Prestador asignado'
    # )
    
    # cantidad_realizadas = fields.Integer("Cant. Realizadas")
    # hora_fin = fields.Integer() # agregar validacion <24
    

    # agenda_ids = fields.One2many('hcd.agenda', 'plan_trabajo_line_id',
    #      string="Agenda",
    # )

    precio = fields.Float("Precio")
    costo = fields.Float("Costo")

    pagador_id = fields.Many2one(
        'res.partner', 'Pagador',)

    observaciones = fields.Char()

    descripcion_view = fields.Html(compute="_get_descripcion_producto_ptlo")

    @api.depends('product_id')
    def _get_descripcion_producto_ptlo(self):
        for rec in self:
            if rec.product_id:
                rec.descripcion_view = rec.product_id.description
