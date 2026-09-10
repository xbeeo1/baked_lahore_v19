# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_edit_analytic_distribution = fields.Boolean(
        string='Allow Edit Analytic Distribution',
        help='If enabled, the user can edit Analytic Distribution on transaction lines.'
    )

    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        'res_users_analytic_account_rel',
        'user_id',
        'analytic_account_id',
        string='Allowed Analytic Accounts',
    )