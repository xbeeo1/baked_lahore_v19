# -*- coding: utf-8 -*-

from odoo import fields, models


class CogsBasis(models.Model):
    _name = "cogs.basis"
    _description = "COGS Basis"

    name = fields.Char(string="Name",required=True)