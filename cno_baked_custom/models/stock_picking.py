# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    _description = 'stock.picking.inherit'


    def button_validate(self):
        for picking in self:
            for move in picking.move_ids:
                if not move.expiry_date:
                    raise ValidationError(
                        _("Please enter Expiry Date for product '%s'.")
                        % move.product_id.display_name
                    )

        return super().button_validate()
