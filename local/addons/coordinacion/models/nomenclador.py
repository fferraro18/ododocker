from odoo import api,fields, models, _
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


#  todas las variables de Nomenclador_costo para generarlos
ETARIO = [('ADULTO','AD'),('PEDIATRICO','PE'),('NEONATO','NE')]
 
PALIATIVO = [('SI','PAL'),('NO','GEN')]

HABIL = [('H','H'),('N','I')]


COMPLEJIDAD = [('A','A'),('B','B')]
    
DISCAPACIDAD = [ ('SI','S'),('NO','N')]

    # zona_geografica_id = fields.Many2one(
    #     comodel_name="hcd.zona_geografica",
    #     string="Zona Geografica",
    # )
    
HORARIO = [ ('DIURNA'),('NOCTURNA')]

def creo_nomenclador_costo(self):
    nomenclador_id = self.id
    nomenclador_desc = self.description
    categoria_id = self.categoria_id.id
    fecha_hoy = datetime.now()
    zonas = self.env['hcd.zona_costos'].search([])
    categoria_nomenclador= self.env['hcd.categoria_nomenclador'].search([('id','=',categoria_id)])
    titulos = categoria_nomenclador.titulos_ids   #cambiar y traer la lista de todos los titulos 
    _logger.info(zonas)
    for etario in ETARIO:
        for paliativo in PALIATIVO:
            for habil in HABIL:
                for complejidad in COMPLEJIDAD:
                    for discapacidad in DISCAPACIDAD:
                        for horario in HORARIO:
                            _logger.info("entra en bucles :  .................")
                            _logger.info(etario)
                            _logger.info(paliativo)
                            _logger.info(discapacidad)
                            _logger.info(horario)
                            for zona in zonas:
                                for titulo in titulos:
                                    _logger.info("entra en titulo :  .................")
                                    _logger.info(titulo)
                                    dic = {
                                        'name' : str(nomenclador_id) + str(etario[1]) + str(paliativo[1]) + str(complejidad[1]) + str(habil[1])  + str(discapacidad[1]) + horario + str(zona.id) + '.' + str(titulo.id),
                                        'description': nomenclador_desc,
                                        'nomenclador_id': nomenclador_id,
                                        'profesion_id' : titulo.id,
                                        'tipo_paciente' : str(etario[0]),
                                        'paliativo' : str(paliativo[0]),
                                        'dia_habil' : str(habil[0]),
                                        'complejidad' : str(complejidad[0]),
                                        'discapacidad' : str(discapacidad[0]),
                                        'zona_costos_id': zona.id,
                                        'dispo_horaria': horario,
                                        'costo': 1


                                        
                                    }
                                    self.env['hcd.nomenclador_costo'].create(dic)

    return True

def creo_servicios_os(self):    
    nomenclador_id = self.id
    nomenclador = self.name
    fecha_hoy = datetime.now()

    clientes_ids = self.env['res.partner'].search([('hcd_type', '=', 'cliente'),('is_company', '=', True),('name', '=', 'IAPOS')])
    for cliente in clientes_ids:
        _logger.info("Entro con cliente :  .................")
        _logger.info(cliente.name)
        codigo = str(cliente.hcd_id)
        if not codigo:
            continue
        dic = {
            'name' : codigo + '.' + nomenclador + '.AD.PAL',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'ADULTO',
            'paliativo' : 'SI',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)
        dic = {
            'name' : codigo + '.' + nomenclador + '.AD.GEN',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'ADULTO',
            'paliativo' : 'NO',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)
        dic = {
            'name' : codigo + '.' + nomenclador + '.PE.PAL',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'PEDIATRICO',
            'paliativo' : 'SI',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)
        dic = {
            'name' : codigo + '.' + nomenclador + '.PE.GEN',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'PEDIATRICO',
            'paliativo' : 'NO',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)
        dic = {
            'name' : codigo + '.' + nomenclador + '.NE.PAL',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'NEONATO',
            'paliativo' : 'SI',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)
        dic = {
            'name' : codigo + '.' + nomenclador + '.NE.GEN',
            'nomenclador_id' : nomenclador_id,
            'obra_social_id' : cliente.id,
            'tipo_paciente' : 'NEONATO',
            'paliativo' : 'NO',
            'fecha_inicio' : fecha_hoy,
            'list_price' : 1,
            'hcd_categ_prod' : 'servicio',
            'detailed_type' : 'service',
            'categ_id' : 1,
            'uom_id' : 1 ,
            'uom_po_id' : 1,
            'sale_line_warn' : 'no-message',
            'purchase_line_warn' : 'no-message',
            'tracking' : 'none'
        }
        
        self.env['product.template'].create(dic)

        #ahora recorro segun los atributos del cliente
        dic = {}
        lista_dic = []
        vip = 0
        nombre = codigo + '.' + nomenclador + '.'
        for etario in ETARIO:
            for paliativo in PALIATIVO:
                dic_elem = crear_dic_base(nomenclador_id, cliente, str(etario[0]), str(paliativo[0]))
                nombre = codigo + '.' + nomenclador + '.' + str(etario[1]) + '.' + str(paliativo[1]) 
                if(cliente.cliente_complejidad):
                    dic_elem = procesar_con_complejidad(self,dic_elem, cliente, nombre, lista_dic)
                else:
                    dic_elem = procesar_sin_complejidad(self,dic_elem, cliente, nombre, lista_dic )
        #_logger.info(lista_dic)
        #self.env['product.template'].create(lista_dic)
        _logger.info("TERMINO DE GRABAR  LA LISTA.....................")
    return True

def procesar_con_complejidad(self,dic, cliente, nombre , lista_dic):
    for complejidad in COMPLEJIDAD:
        dic['complejidad'] = str(complejidad[0])
        if(cliente.cliente_dia_habil):
            procesar_con_dia_habil(self,dic, cliente, nombre , str(complejidad[0]), lista_dic)
        else:
            procesar_sin_dia_habil(self,dic, cliente, nombre , str(complejidad[0]), lista_dic)

def procesar_sin_complejidad(self,dic, cliente, nombre , lista_dic):
    dic['complejidad'] = None
    if(cliente.cliente_dia_habil):
        procesar_con_dia_habil(self,dic, cliente, nombre , '_', lista_dic)
    else:
        procesar_sin_dia_habil(self,dic, cliente, nombre , '_', lista_dic)



def procesar_con_dia_habil(self,dic, cliente, nombre, complejidad, lista_dic):
    for habil in HABIL:
        dic['dia_habil'] = str(habil[0])
        if(cliente.cliente_discapacidad):
            procesar_con_discapacidad(self,dic, cliente, nombre , complejidad, str(habil[1]), lista_dic)
        else:
            procesar_sin_discapacidad(self,dic, cliente, nombre , complejidad, str(habil[1]), lista_dic)


def procesar_sin_dia_habil(self,dic, cliente, nombre, complejidad, lista_dic ):
    dic['dia_habil'] = None
    if(cliente.cliente_discapacidad):
        procesar_con_discapacidad(self,dic, cliente, nombre , complejidad, '_', lista_dic)
    else:
        procesar_sin_complejidad(self,dic, cliente, nombre , complejidad, '_', lista_dic)



def procesar_con_discapacidad(self,dic, cliente, nombre , complejidad, dia_habil,  lista_dic):
    for discapacidad in DISCAPACIDAD:
        dic['discapacidad'] = str(discapacidad[0])
        if(cliente.zona_geografica_id and ( len(cliente.zona_geografica_id) > 0 )):
            procesar_con_zona_geografica(self,dic, cliente, nombre , complejidad, dia_habil,  str(discapacidad[1]), lista_dic)
        else:
            procesar_sin_zona_geografica(self,dic, cliente, nombre , complejidad, dia_habil,  str(discapacidad[1]), lista_dic)

def procesar_sin_discapacidad(self,dic, cliente, nombre , dia_habil, complejidad, lista_dic):
    dic['discapacidad'] = None
    if(cliente.zona_geografica_id and ( len(cliente.zona_geografica_id) > 0 )):
        procesar_con_zona_geografica(self,dic, cliente, nombre , complejidad, dia_habil,  '_' , lista_dic)
    else:
        procesar_sin_zona_geografica(self,dic, cliente, nombre , complejidad, dia_habil,  '_', lista_dic)
    

def procesar_con_zona_geografica(self,dic, cliente, nombre , complejidad, dia_habil,  discapacidad, lista_dic):
    for zona in cliente.zona_geografica_id:
        dic['zona_geografica_id'] = zona.id
        nombre +=  '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + str(zona.id) 
        if cliente.porcentaje_vip:
            nombre += '.' + str(cliente.porcentaje_vip)
        else:
            nombre += '.' + '_'
        dic['name'] = nombre
        self.env['product.template'].create(dic)
        lista_dic.append(dic)
    return True

def procesar_sin_zona_geografica(self,dic, cliente, nombre , dia_habil, complejidad, discapacidad, lista_dic):
    dic['zona_geografica_id'] = None
    nombre +=  '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + '_'
    if cliente.porcentaje_vip:
        dic['porcentaje_vip'] = cliente.porcentaje_vip
        nombre += '.' + str(cliente.porcentaje_vip)
    else:
        dic['porcentaje_vip'] = None
        nombre += '.' + '_'
    dic['name'] = nombre
    self.env['product.template'].create(dic)
    lista_dic.append(dic)
    return True


def crear_dic_base(nomenclador_id, cliente, etario, paliativo):
    return {
        'nomenclador_id' : nomenclador_id,
        'obra_social_id' : cliente.id,
        'tipo_paciente' : etario,
        'paliativo' : paliativo,
        'porcentaje_vip' : cliente.porcentaje_vip,
        'fecha_inicio' : datetime.now(),
        'list_price' : 1,
        'hcd_categ_prod' : 'servicio',
        'detailed_type' : 'service',
        'categ_id' : 1,
        'uom_id' : 1 ,
        'uom_po_id' : 1,
        'sale_line_warn' : 'no-message',
        'purchase_line_warn' : 'no-message',
        'tracking' : 'none'
    }







##########################################################################################################33
            #ahora recorro segun los atributos del cliente
        #     if cliente.cliente_dia_habil or cliente.cliente_complejidad or cliente.cliente_discapacidad:
        #         vip = 0
        #         for etario in ETARIO:
        #             for paliativo in PALIATIVO:
        #                 for habil in HABIL:
        #                     for complejidad in COMPLEJIDAD:
        #                         for discapacidad in DISCAPACIDAD:
        #                             for zona in cliente.zona_geografica_id:
        #                                 nombre = codigo + '.' + nomenclador + '.' + str(etario[1]) + '.' + str(paliativo[1]) + '.' + str(complejidad[1]) + '.'  + str(habil[1]) + '.' + str(discapacidad[1]) + '.' + str(zona.id) + '.' + str(vip)
        #                                 #vals['name'] = id_os + '.' + nombre_nomenclador + '.' + paliativo + '.' + tipo_paciente + '.' + zona + '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + vip
        #                                 _logger.info("entra en bucles  NOMBRE:  .................")
        #                                 _logger.info(nombre)
        #                                 if cliente.porcentaje_vip:
        #                                     nombre = codigo + '.' + nomenclador + '.' + str(etario[1]) + '.' + str(paliativo[1]) + '.' + str(complejidad[1]) + '.'  + str(habil[1]) + '.' + str(discapacidad[1]) + '.' + str(zona.id) + '.' + str(cliente.porcentaje_vip)
        #                                     _logger.info("entra en bucles  NOMBRE VIP:  .................")
        #                                     _logger.info(nombre)
                                
        #                                     dic = {
        #                                         'name' : nombre,
        #                                         'nomenclador_id' : nomenclador_id,
        #                                         'obra_social_id' : cliente.id,
        #                                         'tipo_paciente' : str(etario[0]),
        #                                         'paliativo' : str(paliativo[0]),
        #                                         'dia_habil' : str(habil[0]),
        #                                         'complejidad' : str(complejidad[0]),
        #                                         'discapacidad' : str(discapacidad[0]),
        #                                         'porcentaje_vip' : cliente.porcentaje_vip,
        #                                         'zona_geografica_id' : zona.id,
        #                                         'fecha_inicio' : datetime.now(),
        #                                         'list_price' : 1,
        #                                         'hcd_categ_prod' : 'servicio',
        #                                         'detailed_type' : 'service',
        #                                         'categ_id' : 1,
        #                                         'uom_id' : 1 ,
        #                                         'uom_po_id' : 1,
        #                                         'sale_line_warn' : 'no-message',
        #                                         'purchase_line_warn' : 'no-message',
        #                                         'tracking' : 'none'
        #                                     }
        #                                     self.env['product.template'].create(dic)


        # return True
   





class Nomenclador(models.Model):
    _name = 'hcd.nomenclador'
    # name = fields.Char(string="Nombre", required=True, copy=False,
    #                         readonly=True, default=lambda self: _('New'))

    name = fields.Char(string="Nombre", required=True)
    description = fields.Char("Descripción")
    categoria_id = fields.Many2one(
        comodel_name="hcd.categoria_nomenclador",
        string="Categoria", required = True
    )
    # codigo = fields.Char("Codigo", required = True, size=4)
    nodo = fields.Char("Nodo")

    # Excluye de las estadisticas
    exclude_statistics = fields.Boolean("Excluir de las estadísticas")
    practica_doble = fields.Boolean("Práctica doble")
    active = fields.Boolean("Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre ya existe!'),
        ('description_uniq', 'unique (description)', 'La descripción ya existe!'),
    ]

    @api.model
    def create(self, vals):
        # if vals.get('name', _('New')) == _('New'):
        #     if 'categoria_id' in vals and vals.get('categoria_id', False):
        #         categoria = self.env['hcd.categoria_nomenclador'].browse(vals.get('categoria_id'))
        #         if categoria:
        #             vals['name'] = categoria.prefijo + (self.env['ir.sequence'].next_by_code('nomenclador') or _('New'))
        res = super(Nomenclador, self).create(vals)
        for rec in res:      
            creo_servicios_os(rec)   #tengo que crear el nomenclador nuevo para cada obra social
            creo_nomenclador_costo(res)   #tengo que crear todos los nomenclador_costo para este nuevo nomenclador
            _logger.info("CREO servicios y costos de  NOMENCLADOR:  .................")
            _logger.info(rec.name)
        return rec
    

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     """ _name_search(name='', args=None, operator='ilike', limit=100, name_get_uid=None) -> ids

    #     Private implementation of name_search, allows passing a dedicated user
    #     for the name_get part to solve some access rights issues.
    #     """
    #     _logger.info("entra a la busqueda especifica del servicio .................")
    #     args = list(args or [])
    #     # optimize out the default criterion of ``ilike ''`` that matches everything
    #     if not self._rec_name:
    #         _logger.warning("Cannot execute name_search, no _rec_name defined on %s", self._name)
    #     elif not (name == '' and operator == 'ilike'):
    #         args += [(self._rec_name, operator, name)]
    #     return self._search(args, limit=limit, access_rights_uid=name_get_uid)



    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100):
    #     _logger.info("entra a la busqueda especifica del servicio .................")
    #     args = args or []
    #     recs = self.browse()
    #     if not recs:
    #         recs = self.search([('description', operator, name)] + args, limit=limit)
    #     return recs.name_get()

    # def name_get(self):
    #     res = []
    #     for nom in self:
    #         res.append((nom.id, nom.description))
    #     return res
    
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     _logger.info("entra a la busqueda especifica dentro del nomeclador")
    #     args = args or []
    #     recs = self.browse()
    #     if not recs:
    #         recs = self.search([('nomenclador_id', operator, name)] + args, limit=limit)
    #     return recs.name_get()
