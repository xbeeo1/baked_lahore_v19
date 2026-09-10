# -*- coding: utf-8 -*-

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = [
        'purchase.order.line',
        'analytic.distribution.permission.mixin',
    ]
