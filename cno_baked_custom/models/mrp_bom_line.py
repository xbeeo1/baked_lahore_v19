# -*- coding: utf-8 -*-

from odoo import fields, models, api

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits=(16, 8),
    )