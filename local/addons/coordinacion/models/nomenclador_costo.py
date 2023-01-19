from odoo import api,fields, models, _
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)




class NomencladorCosto(models.Model):
    _name = 'hcd.nomenclador_costo'
    # name = fields.Char(string="Nombre", required=True, copy=False,
    #                         readonly=True, default=lambda self: _('New'))
                            
    name = fields.Char()

    description = fields.Char("Descripción")
    nomenclador_id = fields.Many2one(
        comodel_name="hcd.nomenclador",
        string="Nomenclador", required = True
    )
 
    profesion_id = fields.Many2one(
            comodel_name="hcd.profesion",
            string="Profesion",
        )

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

    zona_costos_id = fields.Many2one(
        comodel_name="hcd.zona_costos",
        string="Zona de costos",
    )
    
    dispo_horaria = fields.Selection([
         ('DIURNA', 'DIURNA'),
         ('NOCTURNA', 'NOCTURNA'),
         ])


    costo = fields.Float("Costo")
    fecha_vigencia_costo = fields.Date()
    vigencia_costo_ids = fields.One2many('hcd.vigencia_costo_nomenclador', 'nomenclador_id',
         string="Vigencia de costos de nomencladores",
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre ya existe!'),
    ]

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         if 'nomenclador_id' in vals and vals.get('nomenclador_id', False):
    #             nomenclador = self.env['hcd.nomenclador'].browse(vals.get('nomenclador_id'))
    #             if nomenclador:
    #                 _logger.info("Nomenclador ....................: ")
    #                 _logger.info(nomenclador)
    #                 vals['name'] = nomenclador.name + '_costo_'  + (self.env['ir.sequence'].next_by_code('nomenclador_costo') or _('New'))
    #                 _logger.info("Nombre nuevo ....................: ")
    #                 _logger.info(vals.get('name'))
    #     super(NomencladorCosto, self).create(vals)
        # if (res):      #tengo que crear el nomenclador nuevo para cada obra social
        #     creo_servicios_os(res)
        # return res
