from dataclasses import field
from odoo import api,fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class ExcepcionCosto(models.Model):
    _name = "hcd.excepcion_costo_prestador"
    _description = "Excepciones de costos"
    name = fields.Char("Descripción de la excepción",required=True)
    prestador_id = fields.Many2one(
        'res.partner', 'Prestador',
        domain="['|',('hcd_type', '=', 'prestador'),('hcd_type', '=', 'efector'),('status', '=', 'activo')]",
        required=True,
        help='Prestador asignado'
    )

    fecha_ini = fields.Date(string="Fec.Ini.",  default=datetime.now(),required=True)
    fecha_fin = fields.Date(string="Fec.Fin",  default=datetime.now(),required=True)

    paciente_id = fields.Many2one(
        'res.partner', 'Paciente',
        domain="[('hcd_type', '=', 'paciente')]",
        help='Paciente asociado al plan de trabajo'
    )
    
    nomenclador_id = fields.Many2one(
        comodel_name="hcd.nomenclador",
        string="Nomenclador")
    # faltan fechas especificas, hay que hacer una tabla externa !
    precio_base = fields.Float("Excepción base", default=0,required=True)
    sadofe_plus = fields.Float("SADOFE plus")
    zona_plus = fields.Float("ZONA plus")
    otro_plus = fields.Float("OTROS plus")
    comentarios = fields.Char("Comentarios")
    active = fields.Boolean("Activo?", default=True)
    date_published = fields.Date()

    @api.onchange('fecha_ini')
    def _check_two_date_ini_excepcion(self):
        for record in self:
                if (record.fecha_ini) and (record.fecha_fin):
                    if record.fecha_ini.strftime('%Y-%m-%d') > record.fecha_fin.strftime('%Y-%m-%d'):
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    
    
    @api.onchange('fecha_fin')
    def _check_two_date_fin_excepcion(self):
        for record in self:
                if (record.fecha_ini) and (record.fecha_fin):
                    if record.fecha_ini.strftime('%Y-%m-%d') > record.fecha_fin.strftime('%Y-%m-%d'):
                        raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin")

    
    
