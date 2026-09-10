from odoo import fields, models, api


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    is_pos_plan = fields.Boolean(string="Is POS Plan")

    @api.model
    def get_relevant_plans(self, **kwargs):
        plans = super().get_relevant_plans(**kwargs)
        if kwargs.get('business_domain') == 'stock_move':
            plans = [p for p in plans if self.browse(p["id"]).is_pos_plan]
        return plans