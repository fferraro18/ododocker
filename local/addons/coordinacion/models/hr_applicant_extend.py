from odoo import api,fields, models

class Hr_applicant_extend(models.Model):
    _inherit = "hr.applicant"
    
    def create_prestador_from_recruitment(self):
        for applicant in self:
            dic = {
                'is_company': False,
                'type': 'contact',
                'hcd_type': 'prestador',
                'status': 'candidato',
                'name': applicant.partner_name,
                'email': applicant.email_from,
                'phone': applicant.partner_phone,
                'mobile': applicant.partner_mobile
            }
            record = self.env['res.partner'].create(dic)
        return


    