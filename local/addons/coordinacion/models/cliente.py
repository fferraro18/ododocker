from odoo.exceptions import ValidationError
from odoo import api, fields, models
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)
import re

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


class Cliente(models.Model):
    _inherit = 'res.partner'

    alcance_cliente = fields.Selection([
        ('regional', 'Regional'),
        ('nacional', 'Nacional')],)

    convenio_id = fields.Many2one(
        'hcd.convenio', 'Convenio',
        help='convenio de la Obra social'
    )

    razon_social = fields.Char("Razón social")
    razon_social_privado = fields.Char("Razón social")

    cliente_nivel = fields.Selection([
        ('obra_social', 'Obra Social'),
        ('prepaga', 'Prepaga'),
        ('art', 'ART'),
        ('laboratorio', 'Laboratorio'),
        ('privado', 'Privado'),
    ])

    fecha_alta = fields.Date('Fecha Alta')

    vendedor_id = fields.Many2one(
        'hr.employee', 'Vendedor',
        help='Vendedor referente'
    )

    ejecutivo_cta_id = fields.Many2one(
        'hr.employee', 'Ejecutivo de Cta',
        help='Ejecutivo de cuenta'
    )

    # TODO no se que es lo que tiene que traer
    lista_precios = fields.Char('Lista de precios')

    # TODO dice que es desplegable, pero no tiene valores
    ejecutivo_cuenta = fields.Selection([
        ('ejecutivo1', 'Ejecutivo 1'),
        ('ejecutivo2', 'Ejecutivo 2')
    ])

    # TODO dice que es desplegable, pero no tiene valores
    campania = fields.Selection([
        ('campania1', 'Campaña 1'),
        ('campania2', 'Campaña 2')
    ])

    # TODO falta alguno mas? decia etc...
    condicion_venta = fields.Selection([
        ('contado', 'Contado'),
        ('dias30', '30'),
        ('dias45', '45'),
        ('dias60', '60'),
        ('dias90', '90')
    ])

    # TODO no dice que contiene el desplegable
    #fc_por_defecto = fields.Selection([
    #   ('factura1', 'Factura 1'),
    #   ('factura2', 'Factura 2'),
    #   ('factura3', 'Factura 3')
    #])

    comision = fields.Integer('Comisión')

    # TODO no habria que ver de modificar la solapa que ya esta???
    mail_comercial = fields.Char('Mail comercial')

    mail_operaciones = fields.Char('Mail operaciones')

    mail_finanzas = fields.Char('Mail Finanzas')

    telefono_comercial = fields.Char('Teléfono comercial')

    telefono_operaciones = fields.Char('Teléfono operaciones')

    telefono_finanzas = fields.Char('Teléfono finanzas')
    # TODO fin no habria que ver de modificar la solapa que ya esta???

    usuario_web_portal = fields.Char('Usuario Web Portal')

    # TODO esto es visible???
    contrasena_web_portal = fields.Char('Contraseña Web Portal')

    descuento = fields.Char('Descuento')

    limite_credito = fields.Integer('Límite crédito')

    # TODO esto es GP Id ???
    numero_cliente = fields.Integer('Número de cliente')

    # TODO no esta esta info en la localizacion argentina??? Donde???

    # TODO ahora hay solo un checkbox, habria que cambiarlo ???
    cliente_estado = fields.Selection([
        ('activo', 'ACTIVO'),
        ('inactivo', 'INACTIVO'),
        ('suspendido', 'SUSPENDIDO')
    ])

    # TODO mostrar solo si 'estado' es 'inactivo'
    cliente_subestado = fields.Selection([
        ('incobrable', 'INCOBRABLE'),
        ('legales', 'LEGALES'),
        ('convenio_vencido', 'CONVENIO VENCIDO')
    ])

    # TODO ya lo tiene
    #cuit = fields.Integer('CUIT')

    # TODO ver como se hace (entidades, pacientes, privados)
    # tipo_cliente = ???

    # TODO es un desplegable pero no dice que contenido tiene
    # categoria_iva = fields.Selection([
    #      ('categoria1', 'Categoría 1'),
    #      ('categoria2', 'Categoría 2'),
    #      ('categoria3', 'Categoría 3'),
    # ])

    codigo_percepciones = fields.Integer('Código')

    provincia_percepciones = fields.Integer('Provincia')

    pocentaje_percepciones = fields.Integer('% Percp')

    exento_percepciones = fields.Boolean('Exento')

    fecha_validez_percepciones = fields.Date()

    # IIGG  usado en proveedores

    retencion_iigg = fields.Selection([
         ('compra_bienes', 'Compra de Bienes'),
         ('locacion', 'Locación de obras y servicios'),
         ('alquiler_equipos', 'Alquiler de equipos'),
         ('honorario_prof_libre', 'Honorarios,Prof Libres'),
         ('fcm', 'Retención FC M'),
         ('fca', 'FC A sujeta a Reten'),
    ])

    cliente_paciente = fields.Boolean(default=False)

    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
        string='Customer Payment Terms',
        domain="[('company_id', 'in', [current_company_id, False])]",
        help="This payment term will be used instead of the default one for sales orders and customer invoices")

    ###  variables relacionadas con la creacion del Servicio

    cliente_dia_habil = fields.Boolean("Día habil")
    cliente_complejidad = fields.Boolean("Complejidad")
    cliente_discapacidad = fields.Boolean("Discapacidad")

    porcentaje_vip = fields.Selection([
        ('0', '0'),
        ('10', '10'),
        ('20', '20'),
        ('30', '30'),
        ('40', '40'),
        ])
 
    zona_geografica_id = fields.Many2many(
         comodel_name="hcd.zona_geografica",  relation='cliente_zona_geografica_rel',
         string="Zona Geográfica",
     )

    _sql_constraints = [
        ('razon_social_uniq', 'unique (razon_social)', 'La Razón Social ya existe!'),
        ('cuit_uniq', 'unique (vat)', 'El CUIT ya existe!'),
        ('dni_uniq', 'unique (dni)', 'El DNI ya existe!'),
    ]


    @api.constrains('cliente_paciente')
    def check_cliente_paciente(self):
        for rec in self:
            if (rec.cliente_paciente):
                rec['hcd_type'] = 'cliente_paciente' 
                _logger.info("Se va a grabar como cliente_paciente !!")


    @api.constrains('vat')
    def check_name(self):
        for rec in self:
            if (rec.vat):
                if not re.match("^[0-9]+$", rec.vat):
                    raise ValidationError('El CUIT debe contener solo números')

    @api.constrains('dni')
    def _check_dni(self):
        for rec in self:
            if (rec.dni):
                if not re.match("^[0-9]+$", rec.dni):
                    raise ValidationError('El DNI debe contener solo números')
                if ( len(rec.dni) > 8) :
                    raise ValidationError('El DNI no puede tener más de 8 cifras')

    @api.constrains('celular')
    def check_celular(self):
        for rec in self:
            if (rec.celular):
                if not re.match("^[0-9]+$", rec.celular):
                    raise ValidationError('El celular debe contener solo números')

    @api.constrains('celular_contacto')
    def check_celular_contacto(self):
        for rec in self:
            if (rec.celular_contacto):
                if not re.match("^[0-9]+$", rec.celular_contacto):
                    raise ValidationError('El celular debe contener solo números')


    @api.constrains('telefono_comercial')  
    def check_telefono_comercial(self):
        for rec in self:
            if (rec.telefono_comercial):
                if not re.match("^[0-9]+$", rec.telefono_comercial):
                    raise ValidationError('El teléfono debe contener solo números')

    @api.constrains('telefono_operaciones')
    def check_telefono_operaciones(self):
        for rec in self:
            if (rec.telefono_operaciones):
                if not re.match("^[0-9]+$", rec.telefono_operaciones):
                    raise ValidationError('El teléfono debe contener solo números')
   
    @api.constrains('telefono_finanzas')
    def check_telefono_finanzas(self):
        for rec in self:
            if (rec.telefono_finanzas):
                if not re.match("^[0-9]+$", rec.telefono_finanzas):
                    raise ValidationError('El teléfono debe contener solo números')


    @api.model
    def create(self, vals):
        res = super(Cliente, self).create(vals)
        if res.hcd_id == 0:
            res.hcd_id = res.id + 918000000
        if vals.get('hcd_type'):
            if vals.get('hcd_type') == 'cliente' and vals.get('company_type') == 'company':
                t = creo_servicios(res)
        
        return res

    def agrego_servicios(self):
        t = creo_servicios(self)


def creo_servicios(self):
        obrasocial_id = self.hcd_id
        codigo = str(self.hcd_id)
        if not obrasocial_id:
            raise ValidationError('Falta el atributo HCD_ID')
        obrasocial = self.name
        nomencladores = self.env['hcd.nomenclador']
        nomencladores_ids = nomencladores.search([])
        lista_servicios = []
        for nomenclador in nomencladores_ids:
            _logger.info("entra en bucles  NOMENCLADOR:  .................")
            _logger.info(nomenclador.name)
            nomenclador_id = nomenclador.id
            nomenclador_name = nomenclador.name
            # creo los 6 por defecto
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.AD.PAL',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'ADULTO',
            #     'paliativo' : 'SI',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # #self.env['product.template'].create(dic)
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.AD.GEN',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'ADULTO',
            #     'paliativo' : 'NO',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # #self.env['product.template'].create(dic)
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.PE.PAL',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'PEDIATRICO',
            #     'paliativo' : 'SI',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # #self.env['product.template'].create(dic)
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.PE.GEN',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'PEDIATRICO',
            #     'paliativo' : 'NO',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # #self.env['product.template'].create(dic)
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.NE.PAL',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'NEONATO',
            #     'paliativo' : 'SI',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # #self.env['product.template'].create(dic)
            # dic = {
            #     'name' : codigo + '.' + nomenclador_name + '.NE.GEN',
            #     'nomenclador_id' : nomenclador_id,
            #     'obra_social_id' : obrasocial_id,
            #     'tipo_paciente' : 'NEONATO',
            #     'paliativo' : 'NO',
            #     'fecha_inicio' : datetime.now(),
            #     'list_price' : 1,
            #     'hcd_categ_prod' : 'servicio',
            #     'detailed_type' : 'service',
            #     'categ_id' : 1,
            #     'uom_id' : 1 ,
            #     'uom_po_id' : 1,
            #     'sale_line_warn' : 'no-message',
            #     'purchase_line_warn' : 'no-message',
            #     'tracking' : 'none'
            # }
            # lista_servicios.append(dic)
            # if len(lista_servicios) != 0:
            #     _logger.info("Yendo a grabar los DEFAULT :  .................")
            #     self.env['product.template'].create(lista_servicios)

            #ahora recorro segun los atributos del cliente
            dic = {}
            lista_dic = []
            vip = 0
            nombre = codigo + '.' + nomenclador_name + '.'
            for etario in ETARIO:
                for paliativo in PALIATIVO:
                    dic_elem = crear_dic_base(self, nomenclador_id, str(etario[0]), str(paliativo[0]))
                    nombre = codigo + '.' + nomenclador_name + '.' + str(etario[1]) + '.' + str(paliativo[1]) 
                    if(self.cliente_complejidad):
                        dic_elem = procesar_con_complejidad(self,dic_elem, nombre, lista_dic)
                    else:
                        dic_elem = procesar_sin_complejidad(self,dic_elem, nombre, lista_dic )
            #_logger.info(lista_dic)
            #self.env['product.template'].create(lista_dic)
            _logger.info("TERMINO DE GRABAR  LA LISTA.....................")
        return True


def procesar_con_complejidad(self,dic, nombre , lista_dic):
    for complejidad in COMPLEJIDAD:
        dic['complejidad'] = str(complejidad[0])
        if(self.cliente_dia_habil):
            procesar_con_dia_habil(self,dic, nombre , str(complejidad[0]), lista_dic)
        else:
            procesar_sin_dia_habil(self,dic, nombre , str(complejidad[0]), lista_dic)

def procesar_sin_complejidad(self,dic, nombre , lista_dic):
    dic['complejidad'] = None
    if(self.cliente_dia_habil):
        procesar_con_dia_habil(self,dic, nombre , '_', lista_dic)
    else:
        procesar_sin_dia_habil(self,dic, nombre , '_', lista_dic)



def procesar_con_dia_habil(self,dic, nombre, complejidad, lista_dic):
    for habil in HABIL:
        dic['dia_habil'] = str(habil[0])
        if(self.cliente_discapacidad):
            procesar_con_discapacidad(self,dic, nombre , complejidad, str(habil[1]), lista_dic)
        else:
            procesar_sin_discapacidad(self,dic, nombre , complejidad, str(habil[1]), lista_dic)


def procesar_sin_dia_habil(self,dic, nombre, complejidad, lista_dic ):
    dic['dia_habil'] = None
    if(self.cliente_discapacidad):
        procesar_con_discapacidad(self,dic, nombre , complejidad, '_', lista_dic)
    else:
        procesar_sin_discapacidad(self,dic, nombre , complejidad, '_', lista_dic)



def procesar_con_discapacidad(self,dic, nombre , complejidad, dia_habil,  lista_dic):
    for discapacidad in DISCAPACIDAD:
        dic['discapacidad'] = str(discapacidad[0])
        if(self.zona_geografica_id and ( len(self.zona_geografica_id) > 0 )):
            procesar_con_zona_geografica(self,dic, nombre , complejidad, dia_habil,  str(discapacidad[1]), lista_dic)
        else:
            procesar_sin_zona_geografica(self,dic, nombre , complejidad, dia_habil,  str(discapacidad[1]), lista_dic)

def procesar_sin_discapacidad(self,dic, nombre , dia_habil, complejidad, lista_dic):
    dic['discapacidad'] = None
    if(self.zona_geografica_id and ( len(self.zona_geografica_id) > 0 )):
        procesar_con_zona_geografica(self,dic, nombre , complejidad, dia_habil,  '_' , lista_dic)
    else:
        procesar_sin_zona_geografica(self,dic, nombre , complejidad, dia_habil,  '_', lista_dic)
    

def procesar_con_zona_geografica(self,dic, nombre , complejidad, dia_habil,  discapacidad, lista_dic):
    for zona in self.zona_geografica_id:
        dic['zona_geografica_id'] = zona.id
        #nombre_cero = nombre
        nombre +=  '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + str(zona.id) 
        #nombre_cero +=  '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + '0' 
        if self.porcentaje_vip:
            nombre += '.' + str(self.porcentaje_vip)
        else:
            nombre += '.' + '_'
        dic['name'] = nombre
        self.env['product.template'].create(dic)
        # if self.porcentaje_vip:    #agrego el porentaje cero 
        #     dic['name'] = nombre_cero
        #     self.env['product.template'].create(dic)
        #     lista_dic.append(dic)
        lista_dic.append(dic)
    return True

def procesar_sin_zona_geografica(self,dic, nombre , dia_habil, complejidad, discapacidad, lista_dic):
    dic['zona_geografica_id'] = None
    nombre +=  '.' + complejidad + '.' + dia_habil + '.' + discapacidad + '.' + '_'
    if self.porcentaje_vip:
        dic['porcentaje_vip'] = self.porcentaje_vip
        nombre += '.' + str(self.porcentaje_vip)
    else:
        dic['porcentaje_vip'] = None
        nombre += '.' + '_'
    dic['name'] = nombre
    self.env['product.template'].create(dic)
    lista_dic.append(dic)
    return True


def crear_dic_base(self, nomenclador_id, etario, paliativo):
    return {
        'nomenclador_id' : nomenclador_id,
        'obra_social_id' : self.id,
        'tipo_paciente' : etario,
        'paliativo' : paliativo,
        'porcentaje_vip' : self.porcentaje_vip,
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
