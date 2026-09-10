# -*- coding: utf-8 -*-

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)

        if (
            payment_vals.get('partner_type') == 'supplier'
            and self.partner_id
            and self.partner_id.commission_payable_id
        ):
            payment_vals['destination_account_id'] = (
                self.partner_id.commission_payable_id.id
            )

        return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        payment_vals = super()._create_payment_vals_from_batch(batch_result)

        partner = self.env['res.partner'].browse(
            payment_vals.get('partner_id')
        )

        if (
            payment_vals.get('partner_type') == 'supplier'
            and partner
            and partner.commission_payable_id
        ):
            payment_vals['destination_account_id'] = (
                partner.commission_payable_id.id
            )

        return payment_vals
