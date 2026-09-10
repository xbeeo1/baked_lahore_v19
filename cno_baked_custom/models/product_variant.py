# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductVariantInherit(models.Model):
    _inherit = 'product.product'

    business_type = fields.Selection([('commission', 'Commission'), ('trading', 'Trading'),('manufacturing', 'Manufacturing')], string='Business Type',
                                     required=True,related='product_tmpl_id.business_type', store=True)
    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor',related='product_tmpl_id.vendor_id', store=True)
    product_owner_id = fields.Many2one(comodel_name='res.partner', string='Product Owner',related='product_tmpl_id.product_owner_id', store=True)
    cogs_basis_id = fields.Many2one(comodel_name='cogs.basis', string='COGS Basis',related='product_tmpl_id.cogs_basis_id', store=True)
    profit_classification_id = fields.Many2one(comodel_name='profit.classification', string='Profit Classification' ,related='product_tmpl_id.profit_classification_id', store=True)
    stream = fields.Char(string='Stream',related='product_tmpl_id.stream', store=True)
    brand = fields.Char(string='Brands',related='product_tmpl_id.brand', store=True)
    payable_suppl_2221001_id = fields.Many2one(comodel_name='account.account', string='2221001 Payable to Supplier (Dr.)', related='product_tmpl_id.payable_suppl_2221001_id',store=True)
    stock_hand_1125001_id = fields.Many2one(comodel_name='account.account', string='1125001 Stock in Hand (Cr.)', related='product_tmpl_id.stock_hand_1125001_id',store=True )
    account_debit_id = fields.Many2one(comodel_name='account.account', string='2223002 Inventory held on b/f Vendors (Dr.)', related='product_tmpl_id.account_debit_id',store=True)
    account_credit_id = fields.Many2one(comodel_name='account.account', string='2223006 Commission based Vendor C/A (Cr.)', related='product_tmpl_id.account_credit_id',store=True)
    commission_based_sale = fields.Many2one(comodel_name='account.account', string='3111001 Commission Based Sale (Dr.)', related='product_tmpl_id.commission_based_sale',store=True)
    commission_asset_cr = fields.Many2one(comodel_name='account.account', string='1125001 Stock In Hand (Dr.)', related='product_tmpl_id.commission_asset_cr',store=True)
    commission_cgs = fields.Many2one(comodel_name='account.account', string='2223006 Commission based Vendor C/A (Dr.)', related='product_tmpl_id.commission_cgs',store=True)
    payable_to_supplier_cr = fields.Many2one(comodel_name='account.account', string='2221001 Payable to Supplier (Cr.)' , related='product_tmpl_id.payable_to_supplier_cr',store=True)
    inventory_vendor_cr = fields.Many2one(comodel_name='account.account', string='2223002 Inventory held on b/f Vendors (Cr.)' , related='product_tmpl_id.inventory_vendor_cr',store=True)
    cost_of_goods_cr = fields.Many2one(comodel_name='account.account', string='4111003 Cost of Goods Sold (Cr.)' , related='product_tmpl_id.cost_of_goods_cr',store=True)
    commission_income = fields.Many2one(comodel_name='account.account', string='3111001 Commission Income', related='product_tmpl_id.commission_income',store=True)
    commission_tax = fields.Many2one(comodel_name='account.account', string='2221008 Commission Tax', related='product_tmpl_id.commission_tax',store=True)
    cost_of_goods_exp_adjustment = fields.Many2one(comodel_name='account.account',
                                                   string='4111003 Cost of Goods Sold (Dr.)', related='product_tmpl_id.cost_of_goods_exp_adjustment',store=True)
    commission_exp_adjustment = fields.Many2one(comodel_name='account.account',
                                                string='2223006 Commission based Vendor C/A (Dr.)', related='product_tmpl_id.commission_exp_adjustment',store=True)
    inventory_vendor_exp_Adjustment_cr = fields.Many2one(comodel_name='account.account',
                                                        string='2223002 Inventory held on b/f Vendors (Cr.)', related='product_tmpl_id.inventory_vendor_exp_Adjustment_cr',store=True)
    expiration_per = fields.Float(string='Expiration %', related='product_tmpl_id.expiration_per',store=True)
    commission_per = fields.Float(string='Commission %',related='product_tmpl_id.commission_per', store=True)

