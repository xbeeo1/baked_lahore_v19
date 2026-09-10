# -*- coding: utf-8 -*-

from odoo import fields, models,api

import re


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    @api.model
    def _get_distribution(self, vals):
        distribution = super()._get_distribution(vals) or {}

        for account in self.env.user.analytic_account_ids:
            distribution[str(account.id)] = 100

        return distribution





