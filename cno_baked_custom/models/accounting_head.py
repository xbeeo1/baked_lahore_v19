# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountingHead(models.Model):
    _name = "accounting.head"
    _description = "Accounting Head"

    name = fields.Char(string="Head",required=True)
    accounting_head_line = fields.One2many("accounting.head.line", "accounting_head_id",
                                          string="Accounting Head Lines")


