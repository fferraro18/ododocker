from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

def buscar_OP_Activa_paciente(self, nro_afiliado_pami):
    #afiliado_con_barra = agregar_barra_nro_afiliado(nro_afiliado_pami)
    planes_trabajo = self.env['hcd.plan_trabajo'].search([('status_pami','=','valida_con_visitas'), ('paciente_id.nro_afiliado','like',nro_afiliado_pami)])
    return planes_trabajo

def buscar_OP_Internado_paciente(self, nro_afiliado_pami):
    #afiliado_con_barra = agregar_barra_nro_afiliado(nro_afiliado_pami)
    planes_trabajo = self.env['hcd.plan_trabajo'].search([('status_pami','=','valida_internacion'), ('paciente_id.nro_afiliado','like',nro_afiliado_pami)])
    return planes_trabajo

class Paciente(models.Model):
    _inherit = 'res.partner'
    
    # la mayoría de los campos están mencionados en prestador.py

    diagnostico_id = fields.Many2one(
        comodel_name='hcd.diagnostico', string='Diagnóstico',
        help='Ultimo diagnóstico'
    )

    obra_social_id = fields.Many2one(
        'res.partner', 'Financiador',
        domain="[('hcd_type', '=', 'cliente'),('cliente_estado','=','activo')]",
        help='Financiador actual del paciente'
    )

    nodo_id = fields.Many2one(
        comodel_name='hcd.nodo', string='Nodo',
        help='Nodo de pertenencia'
    )
    
    internaciones_ids = fields.One2many('hcd.internaciones', 'paciente_id',
         string="Internaciones",
    )

    coordinador_id = fields.Many2one(
        'hr.employee', 'Coordinador',
        #domain="[('department_id', '=', 3)]",
        help='Coordinador referente del Paciente'
    )

    comercial_id = fields.Many2one(
        'hr.employee', 'Comercial',
        help='Comercial referente del Paciente'
    )
    program = fields.Selection([
        ('Pediatria', 'Pediatria'),
        ('Paliativos', 'Paliativos'),
        ('Generales', 'Generales'),
        ('Otros', 'Otros')],
        string="Programa")

    tipo_paciente = fields.Selection([
        ('ADULTO', 'ADULTO'),
        ('PEDIATRICO', 'PEDIATRICO'),
        ('NEONATO', 'NEONATO'),],
        help="Tipo de paciente según su edad")  
        
    paliativo_paciente = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    iva_paciente = fields.Selection([
        ('exento', 'EXENTO'),
        ('gravado', 'GRAVADO'),
        ])

    complejidad = fields.Selection([
        ('A', 'ALTA'),
        ('B', 'BAJA'),
        ])
    
    discapacidad = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ])

    zona_costos_id = fields.Many2one(  #zona de costos !!!
        comodel_name="hcd.zona_costos",
        string="Zona de costos",
    )
    recurso_amparo = fields.Boolean(default=False)
    paciente_con_coseguro = fields.Boolean(default=False)
    paciente_con_financiador = fields.Boolean(default=True)
    estado_paciente = fields.Selection([
        ('activo', 'ACTIVO'),
        ('internado', 'INTERNADO'),
        ('obito', 'OBITO'),
        ('otras_bajas', 'OTRAS BAJAS')],default='activo')

    estado_civil = fields.Selection([
        ('soltero', 'Soltero'),
        ('casado', 'Casado'),
        ('viudo', 'Viudo'),
        ('divorciado', 'Divorciado'),
        ('otro', 'Otro')],)

    nro_afiliado = fields.Char()
    nro_afiliado_barra = fields.Char()
    pami_gp = fields.Integer(default=0)

    @api.onchange('pami_gp')
    def on_change_controlo_gp(self):
        for rec in self:
            if  rec.pami_gp:
                if rec.pami_gp <0 or rec.pami_gp >99:
                    raise ValidationError("GP debe ser un valor entre 0 y 99")

    @api.onchange('estado_paciente')
    def on_change_estado_paciente_pami(self):
        for rec in self:
            _logger.info("Entro por cambio de estado.  Obra social :  ....")
            _logger.info(rec.obra_social_id.name)
            nro_afiliado_pami =  rec.nro_afiliado
            if  rec.obra_social_id and rec.obra_social_id.name == 'INSPJ':    #SUJETO AL NOMBRE DE LA RAZON SOCIAL  ... UN ASCO !!!
                if rec.estado_paciente == 'internado':
                    _logger.info("Entro como Internado")
                    op_activas = buscar_OP_Activa_paciente(self, nro_afiliado_pami)
                    for op in op_activas:
                        op.update({'status_pami': 'valida_internacion'})
                        _logger.info("CAmbio  Estado -> valida internacion!!!!")
                
                if rec.estado_paciente == 'obito':
                    _logger.info("Entro como OBITO")
                    op_activas = buscar_OP_Activa_paciente(self, nro_afiliado_pami)
                    for op in op_activas:
                        op.update({'status_pami': 'valida_obito'})
                        _logger.info("CAmbio  Estado -> valida obito!!!!")

                if rec.estado_paciente == 'otras_bajas':
                    _logger.info("Entro como Internado")
                    op_activas = buscar_OP_Activa_paciente(self, nro_afiliado_pami)
                    for op in op_activas:
                        op.update({'status_pami': 'valida_baja'})
                        _logger.info("CAmbio  Estado -> valida baja!!!!")
                    
                if rec.estado_paciente == 'activo':
                    _logger.info("Entro como Activo")
                    op_activas = buscar_OP_Internado_paciente(self, nro_afiliado_pami)
                    for op in op_activas:
                        op.update({'status_pami': 'valida_con_visitas'})
                        _logger.info("CAmbio  Estado -> valida con visitas!!!!")