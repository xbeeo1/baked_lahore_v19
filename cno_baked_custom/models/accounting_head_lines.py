# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountingHeadLines(models.Model):
    _name = "accounting.head.line"
    _description = "Accounting Head Lines"

    account_id = fields.Many2one(comodel_name='account.account',string="Account",required=True)
    accounting_head_id = fields.Many2one(comodel_name='accounting.head',string="Accounting Head")