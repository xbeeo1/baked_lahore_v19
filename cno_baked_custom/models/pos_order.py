# -*- coding: utf-8 -*-


from odoo import fields, models, tools, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        print('yesssssssssssssssssssssssssssssssssssssssssss')
        move = super()._generate_pos_order_invoice()

        for order in self:
            misc_journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            if order.account_move:
                print('nooooooooooooooooooooooooooooooooooooooooo')
                lines = []
                for line in order.account_move.line_ids:
                    if line.product_id:
                        if line.product_id.business_type == 'commission':
                            credit_value = line.credit
                            debit_value = line.debit
                            if credit_value > 0.0 and line.account_id.id == line.product_id.commission_based_sale.id:
                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.product_id.commission_based_sale.id,
                                    'debit': credit_value,
                                    'credit': 0.0,
                                    'name': 'Revsl/' + move.name,
                                    'partner_id': line.product_id.vendor_id.id,
                                    'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)]
                                }))

                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.product_id.payable_to_supplier_cr.id,
                                    'debit': 0.0,
                                    'credit': credit_value,
                                    'name': line.product_id.name,
                                    'partner_id': line.product_id.vendor_id.id,
                                }))
                            if debit_value > 0.0 and line.account_id.id == line.product_id.cost_of_goods_cr.id:
                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.product_id.cost_of_goods_cr.id,
                                    'debit': 0.0,
                                    'credit': debit_value,
                                    'name': 'Revsl/' + move.name,
                                    'partner_id': line.product_id.vendor_id.id,
                                }))

                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.product_id.commission_cgs.id,
                                    'debit': debit_value,
                                    'credit': 0.0,
                                    'name': line.product_id.name,
                                    'partner_id': line.product_id.vendor_id.id,
                                }))
                    if line.product_id.business_type == 'commission':
                        if line.tax_line_id:
                            credit_value = line.credit
                            debit_value = line.debit
                            if credit_value > 0.0:

                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.account_id.id,
                                    'debit': credit_value,
                                    'credit': 0.0,
                                    'name':  line.name,
                                    'partner_id': None,
                                    'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)]
                                }))
                                for orderline in self.lines.filtered(
                                        lambda lineorder: any(
                                            tax.name == line.name
                                            for tax in lineorder.tax_ids_after_fiscal_position
                                        )
                                    ):
                                    lines.append((0, 0, {
                                        'product_id': line.product_id.id,
                                        'account_id': orderline.product_id.payable_to_supplier_cr.id,
                                        'debit': 0.0,
                                        'credit': orderline.price_subtotal_incl - orderline.price_subtotal,
                                        'name': orderline.product_id.name,
                                        'partner_id': orderline.product_id.vendor_id.id,
                                    }))
                            if debit_value > 0.0:

                                lines.append((0, 0, {
                                    'product_id': line.product_id.id,
                                    'account_id': line.account_id.id,
                                    'debit': 0.0,
                                    'credit': debit_value,
                                    'name':  line.name,
                                    'partner_id': None,
                                    'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)]
                                }))
                                for orderline in self.lines.filtered(
                                        lambda lineorder: any(
                                            tax.name == line.name
                                            for tax in lineorder.tax_ids_after_fiscal_position
                                        )
                                    ):

                                    lines.append((0, 0, {
                                        'product_id': line.product_id.id,
                                        'account_id': orderline.product_id.payable_to_supplier_cr.id,
                                        'debit': orderline.price_subtotal_incl - orderline.price_subtotal,
                                        'credit': 0.0,
                                        'name': orderline.product_id.name,
                                        'partner_id': orderline.product_id.vendor_id.id,
                                    }))

                if lines:
                    move_obj = self.env['account.move'].create({
                        'ref': move.name,
                        'journal_id': misc_journal.id,
                        'move_type': 'entry',
                        'line_ids': lines,
                    })
                    move_obj.action_post()
            orderlines = []
            for lines in order.lines:
                if line.product_id.business_type == 'commission':
                    if lines.product_id.commission_per > 0:
                        base_tag_ids = []
                        tax_tag_ids = []

                        for tax in lines.tax_ids_after_fiscal_position:
                            for repartition_line in tax.invoice_repartition_line_ids:

                                if repartition_line.repartition_type == 'base':
                                    base_tag_ids.extend(repartition_line.tag_ids.ids)

                                elif repartition_line.repartition_type == 'tax':
                                    tax_tag_ids.extend(repartition_line.tag_ids.ids)

                        # duplicates remove
                        base_tag_ids = list(set(base_tag_ids))
                        tax_tag_ids = list(set(tax_tag_ids))
                        if lines.product_id.payable_to_supplier_cr and lines.product_id.commission_income:
                            amount = lines.price_subtotal * (lines.product_id.commission_per/100)
                            orderlines.append((0, 0, {
                                'product_id': lines.product_id.id,
                                'account_id': lines.product_id.payable_to_supplier_cr.id,
                                'debit': amount,
                                'credit': 0.0,
                                'name': 'Revsl/' + move.name,
                                'partner_id': lines.product_id.vendor_id.id,
                            }))

                            orderlines.append((0, 0, {
                                'product_id': lines.product_id.id,
                                'account_id': lines.product_id.commission_income.id,
                                'debit': 0.0,
                                'credit': amount,
                                'name': lines.product_id.name,
                                'partner_id': lines.product_id.vendor_id.id,
                                'tax_tag_ids': [(6, 0, base_tag_ids)],
                            }))
                        if lines.product_id.payable_to_supplier_cr and lines.product_id.commission_tax:
                            amount = lines.price_subtotal * (lines.product_id.commission_per / 100)
                            tax_amount = 0.0
                            for tax in lines.tax_ids_after_fiscal_position:
                                tax_amount += amount * (tax.amount / 100)
                            orderlines.append((0, 0, {
                                'product_id': lines.product_id.id,
                                'account_id': lines.product_id.payable_to_supplier_cr.id,
                                'debit': tax_amount,
                                'credit': 0.0,
                                'name': 'Revsl/' + move.name,
                                'partner_id': lines.product_id.vendor_id.id,
                            }))

                            orderlines.append((0, 0, {
                                'product_id': lines.product_id.id,
                                'account_id': lines.product_id.commission_tax.id,
                                'debit': 0.0,
                                'credit': tax_amount,
                                'name': lines.product_id.name,
                                'partner_id': lines.product_id.vendor_id.id,
                                'tax_tag_ids': [(6, 0, tax_tag_ids)],
                            }))

            if orderlines:
                move_obj = self.env['account.move'].create({
                    'ref': move.name,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': orderlines,
                })
                move_obj.action_post()



        return move
