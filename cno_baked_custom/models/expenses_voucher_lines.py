# -*- coding: utf-8 -*-

from odoo import fields, models,api


class ExpensesVoucherLines(models.Model):
    _name = "expenses.voucher.line"
    _description = "Expenses Voucher Lines"
    _inherit = ['analytic.mixin']

    accounting_head_id = fields.Many2one(comodel_name="accounting.head",string="Accounting Head",required=True)
    account_id = fields.Many2one(comodel_name='account.account',string="Account",required=True,domain="[('id', 'in', available_account_ids)]")
    description=fields.Char(string="Description",required=True)
    amount = fields.Float(string="Amount",required=True)
    expenses_voucher_id = fields.Many2one(comodel_name='expenses.voucher',string="Expense Voucher")

    available_account_ids = fields.Many2many(
        'account.account',
        compute='_compute_available_account_ids'
    )

    @api.depends('accounting_head_id')
    def _compute_available_account_ids(self):
        for rec in self:
            rec.available_account_ids = rec.accounting_head_id.accounting_head_line.mapped('account_id')