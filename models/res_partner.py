from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    total_contracts_price = fields.Monetary(compute='compute_total_contracts_price')

    def compute_total_contracts_price(self):
        """
        total prices of the “confirmed” contracts for this customer.
        """
        for rec in self:
            contracts = self.env['customer.contract'].sudo().search([('partner_id', '=', rec.id), ('state', '=', 'confirmed')])
            rec.total_contracts_price = sum(contracts.mapped('price'))