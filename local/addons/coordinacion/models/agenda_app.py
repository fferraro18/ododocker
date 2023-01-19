
from odoo import api,fields, models, _

class AgendaApp(models.Model):
    _name = 'agenda'

    # es copia de la App !!
    name = fields.Char()  #solo porque es un standar
    # agenda_id = fields.Integer()
    executed = fields.Datetime('Visita realizada')
    # agenda_id = fields.Many2one('hcd.agenda', string='agenda Id')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.executed
            result.append((rec.id, name))
        return result
    