
from odoo.exceptions import ValidationError
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

def busco_costo_nomenclador(self,nomenclador_id):
    for rec in self:
        costo = 0
        #cliente = self.partner_id
        categoria_id = nomenclador_id.categoria_id.id
        categoria_nomenclador= self.env['hcd.categoria_nomenclador'].search([('id','=',categoria_id)])
        titulo = categoria_nomenclador.titulo_defecto_id
        complejidad = self.complejidad
        discapacidad = self.discapacidad
        paliativo = self.paliativo   #  ojo , va a aplicar solo si es paciente ... 
        tipo_paciente = self.tipo_paciente
        zona_id = self.zona_costos_id.id
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
    
        if nomenclador_costo:
            for noc in nomenclador_costo:
                _logger.info("Costo Nomenclador encontrado: ................")
                _logger.info(nomenclador_costo) 
                  #costo = nomenclador_costo.costo
                costo = noc.costo
    return costo

def busco_variables_cliente(self,cliente_id):                 #  ojo que esta solo para complejidad
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

class Modulado(models.Model):
    _inherit = ["mail.thread"]
    _name = 'hcd.modulado'

    name = fields.Char()
    comment = fields.Char("Descripción")

    producto_ids = fields.One2many('hcd.modulado_line', 'modulado_id', string='Servicios')

    obra_social_id = fields.Many2one(
        'res.partner', 'Cliente',
        domain="[('hcd_type', '=', 'cliente')]",
        help='Financiador actual del paciente'
    )
    codigo_cliente = fields.Char("Código interno del cliente")
    codigo_cliente_desc = fields.Char("Descripción del CI del cliente")

    precio = fields.Float("Precio")
    costo = fields.Float("Costo")

    precio_referencia = fields.Float("Precio de referencia", compute='_compute_precio_referencia', store=True)
    costo_referencia = fields.Float("Costo de referencia", compute='_compute_costo_referencia', store=True)

    # necesario para el chatter
    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', string='Followers', groups='base.group_user')

    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')
    message_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        domain=lambda self: [('message_type', '!=', 'user_notification')], auto_join=True)

    modulo_padre = fields.Char("Módulo Padre")

    tipo_paciente = fields.Selection([
        ('ADULTO', 'ADULTO'),
        ('PEDIATRICO', 'PEDIATRICO'),
        ('NEONATO', 'NEONATO'),],
        default='ADULTO',
        help="Tipo de paciente según su edad")  
        
    paliativo = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ],default='NO')

    complejidad = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ],default='B')
    
    discapacidad = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ],default='NO')

    dia_habil = fields.Selection([
        ('H', 'HABIL'),
        ('N', 'NO HABIL'),
        ], default='H')
    
    zona_costos_id = fields.Many2one(
        comodel_name="hcd.zona_costos",
        string="Zona de costo",
    )
    filtro_id = fields.Integer(compute="_get_filtro_id_modulado")     #  para filtrar los servicios 
    utilizar_vigencia = fields.Boolean(default=False)
    vigencia_desde = fields.Date()
    vigencia_hasta= fields.Date()
    estado_producto = fields.Selection([
        ('SIN CREAR', 'SIN CREAR'),
        ('CREADO', 'CREADO')],
        default='SIN CREAR',)

    @api.onchange('vigencia_desde')
    def _check_date_desde_modulado(self):
        for record in self:
                if (record.vigencia_desde) and (record.vigencia_hasta):
                    start_date = record.vigencia_desde.strftime('%Y-%m-%d')
                    end_date = record.vigencia_hasta.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    @api.onchange('vigencia_hasta')
    def _check_date_hasta_modulado(self):
        for record in self:
                if (record.vigencia_desde) and (record.vigencia_hasta):
                    start_date = record.vigencia_desde.strftime('%Y-%m-%d')
                    end_date = record.vigencia_hasta.strftime('%Y-%m-%d')
                    if start_date > end_date:
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    @api.model
    def create(self, vals):
        if not vals.get('producto_ids'):
            raise ValidationError("Debe ingresar al menos un producto o servicio")
        elif ( len(vals.get('producto_ids')) < 1):
            raise ValidationError("Debe ingresar al menos un producto o servicio")
            _logger.info("XXXXXXXXXXXXXXXXX ENTRO Por Create .. Cantidad %s: ", len(vals.get('producto_ids')) )
     
        res = super(Modulado, self).create(vals)
        return res


    @api.onchange('obra_social_id')
    def _get_filtro_id_modulado(self):
        for rec in self:
            rec.filtro_id = 0
            if rec.obra_social_id:
                if (rec.obra_social_id.hcd_type == 'cliente'):   # or (rec.paga_paciente == 'SI'):
                    rec.filtro_id = rec.obra_social_id.id

    
            if rec.obra_social_id:   #voy a buscar si el cliente tiene variables definidas para los costos
                if  (not busco_variables_cliente(self,rec.obra_social_id.id)):
                    rec.discapacidad = None  
                    rec.complejidad = None
                else:
                    rec.discapacidad = rec.obra_social_id.discapacidad
                    rec.complejidad = rec.obra_social_id.complejidad
            _logger.info("Discapacidad : ...... .................")
            _logger.info(rec.discapacidad)


    @api.depends('producto_ids.precio')
    def _compute_precio_referencia(self):
        sumatoria = 0
        for rec in self:
            # _logger.info("precio ref de la linea %s: ", rec.precio)
            # self.precio_referencia += rec.precio
            rec.precio_referencia = 0
            rec.precio = 0
            # sumatoria
            for product_line in self.producto_ids:
                if ( product_line.cantidad == 0 ):
                     raise ValidationError("La cantidad no puede ser cero")
                #_logger.info("el productLine vale %s: ", product_line.product_id.list_price)
                # _logger.info("el productLine precio vale %s: ", product_line.precio)
                # _logger.info("el productLine costo vale %s: ", product_line.costo)
                product_line.precio_referencia = product_line.product_id.list_price 
                if not ( product_line.precio_referencia == 0 ):
                    product_line.porcentaje = 100 * ( product_line.precio / product_line.precio_referencia )


                rec.precio_referencia += product_line.product_id.list_price * product_line.cantidad
                rec.precio += product_line.precio * product_line.cantidad
            _logger.info("sumatoria del precio de referencia %s: ", rec.precio_referencia)
            
    @api.depends('producto_ids.costo')
    def _compute_costo_referencia(self):
        sumatoria = 0
        for rec in self:
            # _logger.info("precio ref de la linea %s: ", rec.precio)
            # self.precio_referencia += rec.precio
            rec.costo_referencia = 0
            rec.costo = 0
            # sumatoria
            for product_line in self.producto_ids:
                if ( product_line.cantidad == 0 ):
                     raise ValidationError("La cantidad no puede ser cero")
                #_logger.info("el productLine vale %s: ", product_line.product_id.list_price)
                # _logger.info("el productLine precio vale %s: ", product_line.precio)
                # _logger.info("el productLine costo vale %s: ", product_line.costo)
                if ( product_line.product_id.hcd_categ_prod == 'servicio' ):
                    nomenclador_id = product_line.product_id.nomenclador_id
                    costo_referencia = busco_costo_nomenclador(self,nomenclador_id)
                else:  
                    costo_referencia = product_line.product_id.costo
                # if ( costo_referencia != 0 ):        #no calculo el porcentaje de los costos
                #     product_line.porcentaje = 100 * ( product_line.precio / product_line.precio_referencia )

                product_line.costo_referencia = costo_referencia
                rec.costo_referencia += costo_referencia * product_line.cantidad
                rec.costo += product_line.costo * product_line.cantidad
            _logger.info("sumatoria del costo de referencia %s: ", rec.costo_referencia)

    def crea_producto(self):   #agregar  modulado_id !!
        for record in self:
            obra_social_id = 1
            if record.obra_social_id:
                obra_social_id = record.obra_social_id.id
            dic = {
                'name' : record.name,
                'description' : record.comment,
                'obra_social_id' : obra_social_id,
                'list_price' : record.precio,
                'costo' : record.costo,
                'hcd_categ_prod' : 'modulado',
                'modulado_id' : record.id,
                'detailed_type' : 'service',
                'categ_id' : 1,
                'uom_id' : 1 ,
                'uom_po_id' : 1,
                'sale_line_warn' : 'no-message',
                'purchase_line_warn' : 'no-message',
                'tracking' : 'none'
                }
            record_linea = self.env['product.template'].create(dic)
            if record_linea:
                record.write({'estado_producto': 'CREADO'})
        return

 

