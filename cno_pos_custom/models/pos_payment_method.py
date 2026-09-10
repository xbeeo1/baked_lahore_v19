# -*- coding: utf-8 -*-


from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position"
    )

    def _load_pos_data_fields(self, config):
        fields = super()._load_pos_data_fields(config)
        fields.append('fiscal_position_id')  # Add your custom field here
        print(fields)
        return fields