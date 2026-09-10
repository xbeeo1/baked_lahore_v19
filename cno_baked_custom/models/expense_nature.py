# -*- coding: utf-8 -*-

from odoo import fields, models


class ExpenseNature(models.Model):
    _name = "expense.nature"
    _description = "Expense Nature"

    name = fields.Char(string="Name",required=True)