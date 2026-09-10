# -*- coding: utf-8 -*-


from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    expense_account_id = fields.Many2one(comodel_name='account.account',string='Expense Account')
    bank_account_id = fields.Many2one(comodel_name='account.account',string='Bank Account')
    charges_per = fields.Float(string='Charges %')