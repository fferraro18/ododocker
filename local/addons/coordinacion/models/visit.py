
from odoo import api,fields, models, _

class Visit(models.Model):
    _name = 'visit'

    # es copia de la App !!
    name = fields.Char()  #solo porque es un standar
    # agenda_id = fields.Integer()
    create_date = fields.Datetime('Fecha de la visita')
    evolution = fields.Char('Evolución')
    
    latitude = fields.Char('Latitud')
    longitude = fields.Char('Longitud')
    location_error = fields.Char('Error de geolocalización')
    
    patient_id = fields.Integer()
    professional_id = fields.Integer()
    ausente_tipo = fields.Char('Ausencia tipo')
    present = fields.Boolean()
    guardia = fields.Boolean()
    guardia_ingreso = fields.Boolean()
    guardia_egreso = fields.Boolean()

    