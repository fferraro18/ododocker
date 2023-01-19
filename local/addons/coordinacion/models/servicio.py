from odoo.exceptions import ValidationError
from odoo import api,fields, models, _
import logging
_logger = logging.getLogger(__name__)

class Practica(models.Model):
    _inherit = "product.template"

    date_published = fields.Date()

    tipo_paciente = fields.Selection([
        ('ADULTO', 'ADULTO'),
        ('PEDIATRICO', 'PEDIATRICO'),
        ('NEONATO', 'NEONATO'),],
        help="Tipo de paciente según su edad")  
        
    paliativo = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    dia_habil = fields.Selection([
        ('H', 'HABIL'),
        ('N', 'NO HABIL'),
        ])

    complejidad = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ])
    
    discapacidad = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    porcentaje_vip = fields.Selection([
        ('0', '0'),
        ('10', '10'),
        ('20', '20'),
        ('30', '30'),
        ('40', '40'),
        ])

    fecha_inicio = fields.Date()
    fecha_fin = fields.Date()

    vigencia_ids = fields.One2many('hcd.vigencia', 'product_id',
         string="Vigencia de precios",
    )

    vigencia_costo_ids = fields.One2many('hcd.vigencia_costo', 'product_id',
         string="Vigencia de costos",
    )

    fecha_vigencia_costo = fields.Date()

    obra_social_id = fields.Many2one(
        'res.partner', 'Cliente',
        domain="[('hcd_type', '=', 'cliente')]",
        help='Cliente'
    )

    nomenclador_id = fields.Many2one(
        comodel_name="hcd.nomenclador",
        string="Nomenclador",
    )

    modulado_id = fields.Many2one(
        comodel_name="hcd.modulado",
        string="Modulado",
    )
    cat_nomenclador_view = fields.Char(string="Cat. Nomen.",compute="_get_categoria_nomenclador")

    zona_geografica_id = fields.Many2one(
        comodel_name="hcd.zona_geografica",
        string="Zona Geografica",
    )



    # TODO ver como se implementa
    #insumes_ids = fields.One2many('product.template', 'insumo_id', string='Insumos')
    # help="Los distintos insumos asociados.")

    authentication_required = fields.Boolean("Requiere Autenticacion")
    
    costo = fields.Float("Costo")
    codigo_cliente = fields.Char("Código interno del cliente")
    codigo_cliente_desc = fields.Char("Descripción del CI del cliente")



    # def name_get(self):
    #     res = []
    #     for activista in self:
    #         name = f'[{activista.name}] {"PPPPPPP"}'
    #         res.append((activista.id, name))
    #     return res
    
    # @api.depends('nomenclador_id')
    # def _get_descripcion_nomenclador(self):
    #     for rec in self:
    #         if rec.nomenclador_id and (rec.nomenclador_id.description != None):
    #             rec.descripcion_view = rec.nomenclador_id.description
    #         else:
    #             rec.descripcion_view = 'Sin nomenclador asociado'


    @api.constrains('costo')
    def _check_something_2(self):
        for record in self:
            if record.costo < 0:
                raise ValidationError('El costo debe ser positivo!')

    @api.constrains('list_price')
    def _check_something(self):
        for record in self:
            if record.list_price < 0:
                raise ValidationError('El precio debe ser positivo!')
    

    @api.constrains('nomenclador_id')
    def _get_categoria_nomenclador(self):
        for record in self:
            record.cat_nomenclador_view = ''
            if record.nomenclador_id and record.nomenclador_id.categoria_id:
                record.cat_nomenclador_view = record.nomenclador_id.categoria_id.name
    
    # def name_get(self):
    #     res = []
    #     for nom in self:
    #         #name = f'[{nom.name}] {nom.description}'
    #         name = f'{nom.description}'
    #         res.append((nom.id, name))
    #     return res

    @api.model
    def create(self, vals):

        categoria = vals.get('hcd_categ_prod')   
        if  categoria :
            if (categoria == 'servicio' ):
                p = vals.get('paliativo') 
                if p == 'SI':
                    paliativo = 'PAL'
                    desc_paliativo = 'PALIATIVO'
                else : 
                    paliativo = 'GEN'
                    desc_paliativo = 'GENERAL'
                    
                tp = vals.get('tipo_paciente')
                if tp == 'ADULTO':
                    tipo_paciente = 'AD'
                    desc_rango = 'ADULTO'
                elif tp == 'PEDIATRICO':
                    tipo_paciente = 'PE'
                    desc_rango = 'PEDIATRICO'
                else :
                    tipo_paciente = 'NE'
                    desc_rango = 'NEONATO'
                
                z = vals.get('zona_geografica_id')
                if z :
                    zona = str(z)
                else :
                    zona = '_'

                c = vals.get('complejidad')
                if c :
                    complejidad = c
                else : 
                    complejidad = '_'   
                    
                h = vals.get('dia_habil')
                if h :
                    dia_habil = h
                else : 
                    dia_habil = '_'


                d = vals.get('discapacidad')
                if d:
                    if d == 'SI':
                        discapacidad = 'S'
                    else : 
                        discapacidad = 'N'
                else : 
                    discapacidad = '_'
                
                v = vals.get('porcentaje_vip')
                if v:
                    vip = v
                else : 
                    vip = '0'
   
                nomenclador = self.env['hcd.nomenclador'].browse(vals['nomenclador_id'])
                nombre_nomenclador = nomenclador.name
                desc_nomenclador = nomenclador.description
                obrasocial = self.env['res.partner'].browse(vals['obra_social_id'])
                id_os = str(obrasocial.hcd_id)
                if id_os:
                    vals['name'] = id_os + '.' + nombre_nomenclador + '.' + tipo_paciente + '.' + paliativo  + '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + zona + '.' + vip
                    vals['description'] = desc_nomenclador + ' ' + desc_rango + ' ' + desc_paliativo
                
                
                #_logger.info("%sXXXXXXXXXXXXXXXXX     ENTRO POr servicio ...  : ")
        res = super(Practica, self).create(vals)
        return res


    #@api.model
    #def create(self,vals):
    #    dic = {
    #        'fecha_inicio' : vals.get('fecha_inicio'),
    #        'fecha_fin' : vals.get('fecha_fin'),
    #        'price' : vals.get('list_price')
    #    }
    #    record = self.env['hcd.vigencia'].create(dic)
    #    return super(Practica, self).create(vals)
    
    #def wiz_open(self):
        # se puede llamar a la accion de la siguiente manera
    #    return self.env['ir.actions.act_window']._for_xml_id("coordinacion.actualizar_precios_action")

        # o sino se puede hacer lo siguiente

        # return {'type': 'ir.actions.act_window', 
        #         'res_model':'hcd.actualizo.precios', 
        #         'view_mode': 'form', 
        #         'target': 'new'}
