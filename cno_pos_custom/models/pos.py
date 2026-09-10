# -*- coding: utf-8 -*-


from odoo import fields, models,tools,api, _


class PosConfig(models.Model):
	_inherit = "pos.config"

	custom_logo = fields.Binary(string='Custom Logo')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_custom_logo = fields.Binary(related="pos_config_id.custom_logo",readonly=False)







class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    vendor_id = fields.Many2one(
        related='product_id.vendor_id',
        string='Vendor',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for vals in vals_list:
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            order = self.env['pos.order'].browse(vals['order_id']) if vals.get('order_id') else False
            if product.create_mrp_order:
                if vals['qty'] > 0:
                    bom_count = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)])
                    if bom_count:
                        bom_temp = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id),
                                                               ('product_id', '=', False)])
                        bom_prod = self.env['mrp.bom'].search([('product_id', '=', vals['product_id'])])
                        if bom_prod:
                            bom = bom_prod[0]
                        elif bom_temp:
                            bom = bom_temp[0]
                        else:
                            bom = []
                        if bom:
                            vals = {
                                'origin': vals['name'],
                                'product_id': product.id,
                                'product_tmpl_id': product.product_tmpl_id.id,
                                'product_uom_id': product.uom_id.id,
                                'product_qty': vals['qty'],
                                'bom_id': bom.id,
                            }
                            mrp = self.env['mrp.production'].sudo().create(vals)
                            if product.done_mrp_order:
                                mrp.button_mark_done()
        return res




