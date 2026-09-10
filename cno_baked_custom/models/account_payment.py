from odoo import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends(
        'journal_id',
        'partner_id',
        'partner_type',
        'partner_id.commission_payable_id',
    )
    def _compute_destination_account_id(self):
        super()._compute_destination_account_id()

        for payment in self:
            if (
                payment.partner_type == 'supplier'
                and payment.partner_id
                and payment.partner_id.commission_payable_id
            ):
                payment.destination_account_id = (
                    payment.partner_id.commission_payable_id
                )
