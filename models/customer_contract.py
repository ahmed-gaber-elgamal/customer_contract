# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerContract(models.Model):
    _name = 'customer.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Customer Contract'

    partner_id = fields.Many2one('res.partner', domain="[('customer_rank', '>', 0)]", required=True, string='Customer',
                                 tracking=True)
    start_date = fields.Date(required=True, tracking=True)
    end_date = fields.Date(required=True, tracking=True)
    price = fields.Float(required=True, tracking=True)
    average_day_price = fields.Float(compute='compute_average_day_price', store=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)
    status_last_change_uid = fields.Many2one('res.users', compute='compute_status_last_change_uid', store=True,
                                             string='Last Change Status By')

    _sql_constraints = [
        ('date_check', "CHECK (start_date <= end_date)", "The start date must be anterior to the end date."),
    ]

    @api.onchange('start_date')
    def onchange_start_date(self):
        self.end_date = False and self.start_date

    @api.depends('state')
    def compute_status_last_change_uid(self):
        for rec in self:
            rec.status_last_change_uid = self.env.user.id

    @api.depends('price', 'start_date', 'end_date')
    def compute_average_day_price(self):
        for rec in self:
            rec.average_day_price = False
            if rec.price and rec.start_date and rec.end_date:
                rec.average_day_price = rec.price / (rec.end_date - rec.start_date).days

    @api.model
    def _check_contract_end_date(self):
        """
            cron job When the end date of a confirmed customer contract comes, automatically change the status to “ended”.
        """
        contracts = self.env['customer.contract'].search([
            ('state', '=', 'confirmed'), ('end_date', '=', fields.Date.today())
        ])
        for contract in contracts:
            contract.state = 'ended'

    def button_confirm(self):
        self.state = 'confirmed'

    def button_cancel(self):
        self.state = 'cancelled'

    def button_draft(self):
        self.state = 'draft'
