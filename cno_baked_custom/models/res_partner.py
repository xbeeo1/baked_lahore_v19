# -*- coding: utf-8 -*-

from odoo import models , api ,fields, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    commission_payable_id = fields.Many2one(
        'account.account',
        string='Commission Payable',
        check_company=True,
        domain="[('account_type', '=', 'liability_current')]",
    )