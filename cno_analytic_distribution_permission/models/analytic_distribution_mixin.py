# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError


class AnalyticDistributionPermissionMixin(models.AbstractModel):
    _name = 'analytic.distribution.permission.mixin'
    _description = 'Analytic Distribution Permission Mixin'

    allow_edit_analytic_distribution = fields.Boolean(
        string='Allow Edit Analytic Distribution',
        compute='_compute_allow_edit_analytic_distribution',
    )

    def _compute_allow_edit_analytic_distribution(self):
        allowed = self.env.user.allow_edit_analytic_distribution
        for record in self:
            record.allow_edit_analytic_distribution = allowed

    def _check_analytic_distribution_write(self, vals):
        if (
            'analytic_distribution' in vals
            and not self.env.context.get('allow_analytic_distribution_write')
            and not self.env.user.allow_edit_analytic_distribution
        ):
            raise AccessError(
                _(
                    'You are not allowed to edit Analytic Distribution.'
                )
            )

    def write(self, vals):
        self._check_analytic_distribution_write(vals)
        return super().write(vals)
