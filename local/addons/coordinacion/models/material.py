from odoo import api, fields, models

class Material(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, vals):
        res = super(Material, self).default_get(vals)
        categories = self.env['product.category'].search([('name', '=', 'Material')])
        if categories:
            res.update({'categ_id': categories[0].id, 'detailed_type': 'product'})
        return res

