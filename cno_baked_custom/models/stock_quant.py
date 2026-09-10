from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        related='product_id.vendor_id',
        store=True,
    )

    cost_price = fields.Float(
        string='Cost Price',
        compute='_compute_cost_price',
        store=True,
    )

    adjustment_cost = fields.Float(
        string='Adjustment Cost',
        compute='_compute_adjustment_cost',
        store=True,
    )

    last_move_date = fields.Datetime(
        string='Last Move Date',
        compute='_compute_last_move_info',
    )

    last_move_quantity = fields.Float(
        string='Last Move Quantity',
        compute='_compute_last_move_info',
    )

    last_move_user_id = fields.Many2one(
        'res.users',
        string='Last Move By',
        compute='_compute_last_move_info',
    )

    @api.depends('product_id', 'product_id.standard_price')
    def _compute_cost_price(self):
        for rec in self:
            rec.cost_price = rec.product_id.standard_price

    @api.depends('cost_price', 'inventory_diff_quantity')
    def _compute_adjustment_cost(self):
        for rec in self:
            rec.adjustment_cost = rec.cost_price * rec.inventory_diff_quantity

    def _compute_last_move_info(self):
        for rec in self:
            move_line = self.env['stock.move.line'].search([
                ('product_id', '=', rec.product_id.id),
                ('state', '=', 'done'),
                ('is_inventory', '=', True),
            ], order='date desc', limit=1)

            rec.last_move_date = move_line.date
            rec.last_move_quantity = move_line.quantity
            rec.last_move_user_id = move_line.create_uid.id