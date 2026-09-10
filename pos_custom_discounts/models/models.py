# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class POsCustomDiscount(models.Model):
    _name = "pos.custom.discount"
    _description = "Pos Custom Discounts"
    _inherit = ["pos.load.mixin"]

    name = fields.Char(string="Name", required=1)
    discount_percent = fields.Float(string="Discount Percentage", required=1)
    description = fields.Text(string="Description")
    available_in_pos = fields.Many2many(
        'pos.config', string="Available In Pos")
    discount_cap = fields.Float('Discount Cap')
    account_debit_id = fields.Many2one(comodel_name='account.account', string="Account Debit")
    account_credit_id = fields.Many2one(comodel_name='account.account', string="Account Credit")
    bank_dis_percent = fields.Float('Bank Discount %')
    vendor_bank_id = fields.Many2one(comodel_name='res.partner', string="Vendor Bank")
    account_journal_id = fields.Many2one(comodel_name='account.journal', string="Account Journal")
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name', 'discount_percent', 'description', 'available_in_pos','discount_cap']

    @api.constrains('discount_percent')
    def check_validation_discount_percent(self):
        """This is to validate discount percentage"""
        if self.discount_percent <= 0 or self.discount_percent > 100:
            raise ValidationError(
                "Discount percent must be between 0 and 100.")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_ids = fields.Many2many('pos.custom.discount')
    allow_custom_discount = fields.Boolean(
        'Allow Customize Discount', default=True)
    allow_security_pin = fields.Boolean('Allow Security Pin')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_discount_ids = fields.Many2many(
        related='pos_config_id.discount_ids', readonly=False)
    pos_allow_custom_discount = fields.Boolean(
        related='pos_config_id.allow_custom_discount', readonly=False)
    pos_allow_security_pin = fields.Boolean(
        related='pos_config_id.allow_security_pin', readonly=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        data = super()._load_pos_data_models(config_id)
        new_model_pos_custom_discount = 'pos.custom.discount'
        if new_model_pos_custom_discount not in data:
            data.append(new_model_pos_custom_discount)
        return data


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    custom_discount_reason = fields.Text('Discount Reason')
    fixed_discount_amount = fields.Float('Fixed Discount Amount')

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += [
            'custom_discount_reason',
            'fixed_discount_amount',
        ]
        return params



class POSOrder(models.Model):
    _inherit = 'pos.order'

    def create_bank_discount_entry(self):
        AccountMove = self.env['account.move']

        for order in self:
            total_amount = 0.0
            debit_account = False
            credit_account = False
            vendor_bank = False

            for line in order.lines:

                if not line.custom_discount_reason:
                    continue

                discount = self.env['pos.custom.discount'].search([
                    ('name', '=', line.custom_discount_reason)
                ], limit=1)

                if not discount:
                    continue

                if not discount.bank_dis_percent:
                    continue

                # Actual discount amount
                line_amount = line.price_unit * line.qty

                discount_amount = (
                        line_amount *
                        line.discount /
                        100
                )

                bank_discount_amount = (
                        discount_amount *
                        discount.bank_dis_percent /
                        100
                )

                total_amount += abs(bank_discount_amount)

                # Accounts / vendor
                debit_account = discount.account_debit_id
                credit_account = discount.account_credit_id
                vendor_bank = discount.vendor_bank_id
                journal_acc = discount.account_journal_id

            if not total_amount:
                continue

            # if not debit_account or not credit_account:
            #     raise ValidationError(
            #         "Debit/Credit account is missing for bank discount."
            #     )

            # if not vendor_bank:
            #     raise ValidationError(
            #         "Vendor Bank is missing for bank discount."
            #     )

            # misc_journal = self.env['account.journal'].search([
            #     ('type', '=', 'general')
            # ], limit=1)
            #
            # if not misc_journal:
            #     raise ValidationError(
            #         "Miscellaneous journal not found."
            #     )

            lines = [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'account_id': debit_account.id,
                    'debit': total_amount,
                    'credit': 0.0,
                    'name':  discount.name + '/' + order.name,
                    'partner_id': vendor_bank.id,
                }),
                (0, 0, {
                    'product_id': line.product_id.id,
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': total_amount,
                    'name': discount.name + '/' + order.name,
                    'partner_id': vendor_bank.id,
                }),
            ]

            move = AccountMove.create({
                'ref': discount.name + '/' + order.name,
                'journal_id': journal_acc.id,

                'move_type': 'entry',
                'line_ids': lines,
            })

            move.action_post()

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()

        self.create_bank_discount_entry()

        return res