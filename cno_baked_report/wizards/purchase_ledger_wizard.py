# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseLedgerWizard(models.TransientModel):
    _name = 'purchase.ledger.wizard'
    _description = 'Purchase Base Ledger Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.context_today,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        domain="[('supplier_rank', '>', 0)]",
    )
    account_ids = fields.Many2many(
        'account.account',
        string='Accounts',
        default=lambda self: self._default_account_ids(),
    )
    report_type = fields.Selection(
        selection=[
            ('purchase', 'Purchase'),
        ],
        string='Report Type',
        default='purchase',
        required=True,
    )

    @api.model
    def _default_account_ids(self):
        """Default account: code 2223006 for the current company."""
        account = self.env['account.account'].search(
            [('code', '=', '2223006')],
            limit=1,
        )
        return [(6, 0, account.ids)] if account else False

    def action_print_report(self):
        self.ensure_one()
        data = {
            'wizard_id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_id': self.partner_id.id,
            'account_ids': self.account_ids.ids,
            'report_type': self.report_type,
        }
        return self.env.ref(
            'cno_baked_report.action_report_purchase_ledger'
        ).report_action(self, data=data)
