# -*- coding: utf-8 -*-


from odoo import fields, models,tools,api, _



class ProductTemplate(models.Model):
    _inherit = "product.template"

    create_mrp_order = fields.Boolean("To Create MRP Order")
    done_mrp_order = fields.Boolean("Done MRP Order")