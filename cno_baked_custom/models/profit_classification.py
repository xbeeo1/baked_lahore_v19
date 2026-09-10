# -*- coding: utf-8 -*-

from odoo import fields, models


class ProfitClassification(models.Model):
    _name = "profit.classification"
    _description = "Profit Classification"

    name = fields.Char(string="Name",required=True)