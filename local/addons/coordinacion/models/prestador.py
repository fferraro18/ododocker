from odoo import api,fields,models
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class Prestador(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char('Nombre')  
    last_name= fields.Char('Apellido')
    

    matricula_nac = fields.Char()  
    matricula_prov = fields.Char()
    matricula_prov_entidad = fields.Char()
    
    #hcd_type = fields.Char()        # valores : paciente | prestador | efector | tecnico | cliente | cliente_paciente 

    hcd_type = fields.Selection([
        ('paciente', 'Paciente'),
        ('prestador', 'Prestador'),
        ('efector', 'Efector'),
        ('tecnico', 'Técnico'),
        ('cliente', 'Cliente'),
        ('cliente_paciente', 'Cliente/Paciente'),
        ('proveedor', 'Proveedor'),
        ('otro', 'Otro')],)
    hcd_sucursal = fields.Char()    # se utilizará para relacionar con HCe
    hcd_id = fields.Integer(default=0)       # se utilizará para relacionar con HCe
    

    es_grupo = fields.Boolean("Es Grupo", default=False)

    contabiliza = fields.Boolean("Contabiliza?", default=True)

    dni = fields.Char("DNI") 
    dni_tipo = fields.Selection([
        ('DNI', 'DNI'),
        ('DI', 'DI'),
        ('LC', 'LC'),
        ('OTRO', 'OTRO')],
        default='DNI',)

    celular = fields.Char("Celular") 
    celular_contacto = fields.Char("Celular de contacto") 
    days_to_pay = fields.Integer('Día de Pago') # agregar validacion <31
    penalty_day = fields.Integer('Día de pago - Penalización') # agregar validacion <31
    forma_pago= fields.Selection([
        ('CH','Cheque'),
        ('DE','Depósito'),
        ('EF','Efectivo'),
        ('TR','Transferencia'),])

    gender = fields.Selection([
        ('femenino', 'Femenino'),
        ('masculino', 'Masculino'),
        ('mujer_trans', 'Mujer Trans'),
        ('varon_trans', 'Varón Trans'),
        ('no_binario', 'No Binario'),
        ('otro', 'Otro')],)
    specialty = fields.Selection([
        ('CLINICA MEDICA', 'CLINICA MEDICA'),
        ('PEDIATRIA', 'PEDIATRIA'),
        ('CUIDADOS PALIATIVOS', 'CUIDADOS PALIATIVOS'),
        ('CIRUGIA GENERAL', 'CIRUGIA GENERAL'),
        ('CARDIOLOGIA', 'CARDIOLOGIA'),
        ('NEUROLOGIA', 'NEUROLOGIA'),
        ('GASTROENTEROLOGIA', 'GASTROENTEROLOGIA'),
        ('OFTALMOLOGIA', 'OFTALMOLOGIA'),
        ('TRAUMATOLOGIA', 'TRAUMATOLOGIA'),
        ('DERMATOLOGIA', 'DERMATOLOGIA'),
        ('OTRA','OTRA')],
        help="Type of the exception activity on record.")  

    scoring = fields.Selection([
        ('0', 'Muy Baja'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy Alta')],
        help="Type of the exception activity on record.")
    
    status = fields.Selection([
        ('candidato', 'CANDIDATO'),
        ('activo', 'ACTIVO'),
        ('suspendido', 'SUSPENDIDO'),
        ('inactivo', 'INACTIVO')],
        default='activo',
        string="Estado")

        

    paliativo_prestador = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('AMBOS', 'AMBOS'),])

    fecha_alta = fields.Date('Fecha de Ingreso', default=datetime.now())
    fecha_baja = fields.Date('Fecha de Inactividad')
    motivo_baja = fields.Selection([
        ('DE', 'DESPIDO'),
        ('FA', 'FALLECIMIENTO'),
        ('LE', 'LICENCIA POR ENFERMEDAD'),
        ('LM', 'LICENCIA POR MATERNIDAD'),
        ('MD', 'MAL DESEMPEÑO'),
        ('RL', 'RECLAMO LEGAL'),
        ('RE', 'RENUNCIA'),
        ('SC', 'SIN CONTACTO'),
        ('SD', 'SIN DISPONIBILIDAD'),
        ('SM', 'SIN MOTIVO'),],
        string="Motivos de Inactividad") 

    motivo_baja_paciente = fields.Selection([
        ('FA', 'FALLECIMIENTO'),
        ('MD', 'MAL DESEMPEÑO'),
        ('RL', 'RECLAMO LEGAL'),
        ('RE', 'RENUNCIA'),
        ('SC', 'SIN CONTACTO'),
        ('SM', 'SIN MOTIVO'),],
        string="Motivos de Baja") 

    place_of_birth = fields.Char('Place of Birth')   # groups="hr.group_hr_user", tracking=True)
    birthday = fields.Date('Date of Birth')          # groups="hr.group_hr_user", tracking=True)
    person_age = fields.Char(string="Edad (años)", compute="_get_age_from_person")

    zona_cobertura_pres_id = fields.Many2many(
             comodel_name="hcd.zona_cobertura", relation='prestador_zona_cobertura_pres_rel',
             string="Zona de cobertura",
         )

    profesion_id = fields.Many2one(
            comodel_name="hcd.profesion",
            string="Profesion",
        )

    sadofe = fields.Selection([
        ('SI', 'SI'),
         ('NO', 'NO'),
         ])
 
    poblacion_asistida_ids = fields.Many2many(
             comodel_name="hcd.poblacion_asistida", relation='prestador_poblacion_asistida_rel',
             string="Población asistida",
         )
 

    cat_nomenclador_ids = fields.Many2many(
             comodel_name="hcd.categoria_nomenclador", relation='prestador_categoria_nomenclador_rel',
             string="Categoria Nomenclador",
         )
 
    dispo_horaria = fields.Selection([
         ('DIURNA', 'DIURNA'),
         ('NOCTURNA', 'NOCTURNA'),
         ('DIURNA_NOCTURNA', 'DIURNA y NOCTURNA'),
         ])
     
    direccion_altura = fields.Char('Altura')
    direccion_pisodpto = fields.Char('Piso y Dpto')
    direccion_barrio = fields.Char('Barrio')
    direccion_partido = fields.Char('Partido/Dpto/Comuna')
    
    mnea = fields.Selection([
        ('PI', 'Primario incompleto'),
        ('PC', 'Primario completo'),
        ('SC', 'Secundario incompleto'),
        ('SI', 'Secundario completo'),
        ('TC', 'Terciario incompleto'),
        ('TI', 'Terciario completo'),
        ('UI', 'Universitario incompleto'),
        ('UC', 'Universitario completo'),
        ('DI', 'Posgrado o doctorado incompleto'),
        ('DC', 'Posgrado o doctorado completo'),
        ])
 
    seguro_mala_praxis = fields.Selection([
         ('SI', 'SI'),
         ('NO', 'NO'),
         ('desconocido', 'Se desconoce'),
         ])
    facturacion_obs = fields.Char('Obs. a facturación')
    auditoria_obs = fields.Char('Obs. de Auditoria')
    tipo_factura_id = fields.Many2one('l10n_latam.document.type', 'Factura tipo', index=True)

    #l10n_ar_afip_responsibility_type_id = fields.Many2one(
     #   comodel_name="l10n_ar_afip_responsibility_type",
     #   string="Responsabilidad AFIP",
     #   )

    @api.depends('birthday')
    def _get_age_from_person(self):
        for rec in self:
            if self.birthday:
                edad = relativedelta(datetime.now(), self.birthday)
                rec.person_age = edad.years
            else:
                rec.person_age="No se puede estimar"

    @api.onchange('first_name')
    def _cambio_nombre(self):
        for rec in self:
            if rec.last_name:
                if rec.first_name:
                    rec.name = rec.last_name.upper() + ", " + rec.first_name
    
    @api.onchange('last_name')
    def _cambio_apellido(self):
        for rec in self:
            if rec.last_name:
                if rec.first_name:
                    rec.name = rec.last_name.upper() + ", " + rec.first_name
    @api.model
    def create(self, vals):
        if vals.get('last_name'):
            if vals.get('first_name'):
                vals['name'] = vals.get('last_name').upper() + ", " + vals.get('first_name')


        res = super(Prestador, self).create(vals)
        if not res.hcd_id:
            res.hcd_id = res.id
        return res


    @api.constrains('days_to_pay')
    def _check_date_end(self):
        for record in self:
            if record.days_to_pay > 41 :
                raise ValidationError("El dia de pago no puede ser mayor a 31")
        # all records passed the test, don't return anything

    def name_get(self):
        res = []
        for nom in self:
            if ( nom.hcd_type == 'efector' ) or ( nom.hcd_type == 'tecnico' ):
                name = f'{nom.name} [{nom.hcd_type}]'
                #name = f'[{nom.name}] {nom.description}'
                #name = f'{nom.description}'
                res.append((nom.id, name))
            else:
                name = nom.name
                res.append((nom.id, name))
            
        return res