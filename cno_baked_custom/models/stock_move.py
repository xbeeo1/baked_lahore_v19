# -*- coding: utf-8 -*-

from odoo import fields, models , api
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = ['stock.move',"analytic.mixin"]

    expiry_date = fields.Date(string='Expiry Date')
    Qty = fields.Float(string='Qty')
    scrap_id = fields.Many2one(comodel_name='stock.scrap', string='Scrap')
    allocation_state = fields.Selection([('draft','Draft'),('done','Done')], default='draft', string='Allocation Status')

    picking_code = fields.Selection(
        related='picking_type_id.code',
        store=True
    )

    scrap_created = fields.Boolean(default=False)

    def _get_plan_domain(self, plan):
        domain = super()._get_plan_domain(plan)
        return domain + [("plan_id.is_pos_plan", "=", True)]

    def action_create_scrap(self):
        self.ensure_one()

        if self.Qty <= 0:
            raise UserError("Qty should be greater than 0!")
        scrap = self.env['stock.scrap'].create({
            'product_id': self.product_id.id,
            'scrap_qty': self.Qty,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_dest_id.id,
            'origin': self.origin or self.name,
            'picking_id': False,
            'analytic_distribution': self.analytic_distribution,
        })

        self.scrap_created = True
        self.scrap_id = scrap.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.scrap',
            'view_mode': 'form',
            'res_id': scrap.id,
            'target': 'current',
        }



