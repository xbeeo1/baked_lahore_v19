import base64
import io
import os
from odoo import models
from datetime import timedelta
from odoo.exceptions import UserError

dirname = os.path.dirname(__file__)


class SaleAnalysisXlsx(models.AbstractModel):
    _name = 'report.cno_baked_report.sale_analysis_report_id_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, report):
        sheet = workbook.add_worksheet('Sale Analysis Report')

        center = workbook.add_format({'align': 'center'})
        center_left = workbook.add_format({'align': 'left'})
        center_right = workbook.add_format({'align': 'right'})

        bold = workbook.add_format({
            'bold': True,
            'align': 'center'
        })

        bold_left = workbook.add_format({
            'bold': True,
            'align': 'left'
        })

        bold_right = workbook.add_format({
            'bold': True,
            'align': 'right'
        })

        date_style_1 = workbook.add_format({
            'text_wrap': True,
            'num_format': 'dd-mm-yyyy',
            'align': 'center',
            'font_size': 10,
            'bold': True,
        })

        date_style = workbook.add_format({
            'num_format': 'dd-mm-yyyy',
            'align': 'center',
        })

        format3_colored = workbook.add_format({
            'align': 'center',
            'bg_color': '#87CEEB',
            'bold': True,
            'font_color': 'white'
        })

        format3_colored_left = workbook.add_format({
            'align': 'left',
            'bg_color': '#87CEEB',
            'bold': True,
            'font_color': 'white'
        })

        format3_colored_right = workbook.add_format({
            'align': 'right',
            'bg_color': '#87CEEB',
            'bold': True,
            'font_color': 'white'
        })

        res_company = self.env.user.company_id
        sheet.set_column('A:V', 20)

        r = 1
        co = 0
        row = 3

        # Formatting the date from and to
        f_date = (
            (report.date_from) + timedelta(hours=5)
        ).strftime("%d-%m-%Y %H:%M:%S")

        t_date = (
            (report.date_to) + timedelta(hours=5)
        ).strftime("%d-%m-%Y %H:%M:%S")

        sheet.merge_range(
            r,
            co,
            r,
            co + 6,
            'Sale Analysis Report',
            bold
        )

        r += 1

        sheet.merge_range(
            r,
            co,
            r,
            co + 6,
            f'Date From:  {f_date}  Date To:  {t_date}',
            date_style_1
        )

        # Query pos.orders within the specified date range
        pos_orders = self.env['pos.order'].search([
            ('date_order', '>=', report.date_from),
            ('date_order', '<=', report.date_to)
        ])

        if not pos_orders:
            raise UserError(
                "No POS orders found in the specified date range."
            )

        # Column headers
        r += 2

        sheet.write(row, 0, 'Date', format3_colored)
        sheet.write(row, 1, 'Time', format3_colored)
        sheet.write(row, 2, 'POS Session', format3_colored)
        sheet.write(row, 3, 'Receipt Number', format3_colored)
        sheet.write(row, 4, 'Receipt Type', format3_colored)
        sheet.write(row, 5, 'Vendor', format3_colored)
        sheet.write(row, 6, 'Stream', format3_colored)
        sheet.write(row, 7, 'Brands', format3_colored)
        sheet.write(row, 8, 'Category', format3_colored)
        sheet.write(row, 9, 'SKU', format3_colored)
        sheet.write(row, 10, 'Item', format3_colored)
        sheet.write(row, 11, 'Quantity', format3_colored)
        sheet.write(row, 12, 'Gross sales', format3_colored)
        sheet.write(row, 13, 'Discount Name', format3_colored)
        sheet.write(row, 14, 'Discount %', format3_colored)
        sheet.write(row, 15, 'Discount Amt', format3_colored)
        sheet.write(row, 16, 'Net sales', format3_colored)
        sheet.write(row, 17, 'Unit Cost/Vendor Cost', format3_colored)
        sheet.write(row, 18, 'COGS/Vendor Cost', format3_colored)
        sheet.write(row, 19, 'Item Gross Profit', format3_colored)
        sheet.write(row, 20, 'Item Profit Margin %', format3_colored)
        sheet.write(row, 21, 'Tax Rate (POS)', format3_colored)
        sheet.write(row, 22, 'Tax Amount', format3_colored)
        sheet.write(row, 23, 'Commission Rate', format3_colored)
        sheet.write(row, 24, 'Commission Income', format3_colored)
        sheet.write(row, 25, 'Vendor Basis', format3_colored)
        sheet.write(row, 26, 'COGS Basis', format3_colored)
        sheet.write(row, 27, 'Profit Classification', format3_colored)
        sheet.write(row, 28, 'Invoice QR', format3_colored)
        sheet.write(row, 29, 'MOP', format3_colored)
        sheet.write(row, 30, 'Store', format3_colored)
        sheet.write(row, 31, 'Cashier Name', format3_colored)
        sheet.write(row, 32, 'Customer Name', format3_colored)
        sheet.write(row, 33, 'Customer Contacts', format3_colored)

        row += 1

        # Grand totals
        grand_quantity = 0
        grand_gross_sales = 0
        grand_discount = 0
        grand_discount_amt = 0
        grand_net_sales = 0
        grand_unit_cost = 0
        grand_cogs = 0
        grand_gross_profit = 0
        grand_tax_amount = 0
        grand_commission_income = 0
        grand_vendor_basis = 0

        # Loop through POS orders
        for order in pos_orders:

            payment_methods = []

            for pay in order.payment_ids:
                mop = pay.payment_method_id.name
                payment_methods.append(mop)

            payment_methods_str = ', '.join(payment_methods)

            # Order totals
            order_quantity = 0
            order_gross_sales = 0
            order_discount = 0
            order_discount_amt = 0
            order_net_sales = 0
            order_unit_cost = 0
            order_cogs = 0
            order_gross_profit = 0
            order_tax_amount = 0
            order_commission_income = 0
            order_vendor_basis = 0

            # Loop through order lines
            for line in order.lines:

                date = (
                    (order.date_order) + timedelta(hours=5)
                ).strftime("%d-%m-%Y")

                time = (
                    (order.date_order) + timedelta(hours=5)
                ).strftime("%H:%M")

                vendor_name = (
                    line.product_id.vendor_id.name
                    if line.product_id.vendor_id
                    else ''
                )

                cogs_b = (
                    line.product_id.cogs_basis_id.name
                    if line.product_id.cogs_basis_id
                    else ''
                )

                pro_classi = (
                    line.product_id.profit_classification_id.name
                    if line.product_id.profit_classification_id
                    else ''
                )

                customer_name = (
                    order.partner_id.name
                    if order.partner_id
                    else ''
                )

                customer_contact = (
                    order.partner_id.phone
                    if order.partner_id
                    else ''
                )

                receipt_type = (
                    'Refund'
                    if order.amount_total < 0
                    else 'Sale'
                )

                gross_sales = line.qty * line.price_unit

                discount_amt = (
                    line.discount * gross_sales
                ) / 100

                net_sale = gross_sales - discount_amt

                cost_goods = (
                    line.qty *
                    line.product_id.standard_price
                )

                gross_profit = net_sale - cost_goods

                taxes = (
                    line.price_subtotal_incl -
                    line.price_subtotal
                )

                if order.amount_total < 0:
                    taxes = -1 * taxes

                tax_per = ', '.join(
                    f"{tax.amount}%"
                    for tax in line.tax_ids_after_fiscal_position
                )

                commission_income = (
                    gross_sales *
                    (line.product_id.commission_per / 100)
                )

                vendor_basis = (
                    gross_profit -
                    (
                        gross_profit *
                        (line.product_id.commission_per / 100)
                    )
                )

                # Write line data
                sheet.write(row, 0, date, center_left)
                sheet.write(row, 1, time, center_left)
                sheet.write(row, 2, order.session_id.name, center_left)
                sheet.write(row, 3, order.name, center_left)
                sheet.write(row, 4, receipt_type, center_left)
                sheet.write(row, 5, vendor_name, center_left)
                sheet.write(row, 6, line.product_id.stream, center_left)
                sheet.write(row, 7, line.product_id.brand, center_left)
                sheet.write(row, 8, line.product_id.categ_id.name, center_left)
                sheet.write(row, 9, line.product_id.default_code, center_left)
                sheet.write(row, 10, line.product_id.name, center_left)
                sheet.write(row, 11, line.qty, center_right)
                sheet.write(row, 12, gross_sales, center_right)
                sheet.write(row, 13, line.custom_discount_reason, center_left)
                sheet.write(row, 14, line.discount, center_right)
                sheet.write(row, 15, discount_amt, center_right)
                sheet.write(row, 16, net_sale, center_right)
                sheet.write(
                    row,
                    17,
                    line.product_id.standard_price,
                    center_right
                )
                sheet.write(row, 18, cost_goods, center_right)
                sheet.write(row, 19, gross_profit, center_right)

                sheet.write(
                    row,
                    20,
                    f"{round((gross_profit / net_sale) * 100) if net_sale else 0}%",
                    center_right
                )

                sheet.write(row, 21, tax_per, center_right)
                sheet.write(row, 22, taxes, center_right)

                sheet.write(
                    row,
                    23,
                    f"{line.product_id.commission_per}%",
                    center_right
                )

                sheet.write(
                    row,
                    24,
                    commission_income,
                    center_right
                )

                sheet.write(
                    row,
                    25,
                    vendor_basis,
                    center_right
                )

                sheet.write(row, 26, cogs_b, center_right)
                sheet.write(row, 27, pro_classi, center_right)
                sheet.write(row, 28, order.invoice_number, center_right)
                sheet.write(row, 29, payment_methods_str, center_left)
                sheet.write(
                    row,
                    30,
                    order.session_id.config_id.name,
                    center_left
                )
                sheet.write(
                    row,
                    31,
                    order.user_id.name,
                    center_left
                )
                sheet.write(row, 32, customer_name, center_left)
                sheet.write(row, 33, customer_contact, center_left)

                # ==========================
                # ORDER TOTAL CALCULATION
                # ==========================

                order_quantity += line.qty
                order_gross_sales += gross_sales
                order_discount += line.discount
                order_discount_amt += discount_amt
                order_net_sales += net_sale
                order_unit_cost += line.product_id.standard_price
                order_cogs += cost_goods
                order_gross_profit += gross_profit
                order_tax_amount += taxes
                order_commission_income += commission_income
                order_vendor_basis += vendor_basis

                row += 1

            # ==========================
            # ORDER TOTAL ROW
            # ==========================

            sheet.write(
                row,
                0,
                'ORDER TOTAL',
                bold_left
            )


            sheet.write(
                row,
                11,
                order_quantity,
                bold_right
            )

            sheet.write(
                row,
                12,
                order_gross_sales,
                bold_right
            )

            sheet.write(
                row,
                14,
                order_discount,
                bold_right
            )

            sheet.write(
                row,
                15,
                order_discount_amt,
                bold_right
            )

            sheet.write(
                row,
                16,
                order_net_sales,
                bold_right
            )

            sheet.write(
                row,
                17,
                order_unit_cost,
                bold_right
            )

            sheet.write(
                row,
                18,
                order_cogs,
                bold_right
            )

            sheet.write(
                row,
                19,
                order_gross_profit,
                bold_right
            )

            sheet.write(
                row,
                22,
                order_tax_amount,
                bold_right
            )

            sheet.write(
                row,
                24,
                order_commission_income,
                bold_right
            )

            sheet.write(
                row,
                25,
                order_vendor_basis,
                bold_right
            )

            # ==========================
            # ADD TO GRAND TOTAL
            # ==========================

            grand_quantity += order_quantity
            grand_gross_sales += order_gross_sales
            grand_discount += order_discount
            grand_discount_amt += order_discount_amt
            grand_net_sales += order_net_sales
            grand_unit_cost += order_unit_cost
            grand_cogs += order_cogs
            grand_gross_profit += order_gross_profit
            grand_tax_amount += order_tax_amount
            grand_commission_income += order_commission_income
            grand_vendor_basis += order_vendor_basis

            row += 2

        # ==========================
        # GRAND TOTAL ROW
        # ==========================

        sheet.write(
            row,
            0,
            'GRAND TOTAL',
            format3_colored_left
        )

        sheet.write(
            row,
            11,
            grand_quantity,
            format3_colored_right
        )

        sheet.write(
            row,
            12,
            grand_gross_sales,
            format3_colored_right
        )

        sheet.write(
            row,
            14,
            grand_discount,
            format3_colored_right
        )

        sheet.write(
            row,
            15,
            grand_discount_amt,
            format3_colored_right
        )

        sheet.write(
            row,
            16,
            grand_net_sales,
            format3_colored_right
        )

        sheet.write(
            row,
            17,
            grand_unit_cost,
            format3_colored_right
        )

        sheet.write(
            row,
            18,
            grand_cogs,
            format3_colored_right
        )

        sheet.write(
            row,
            19,
            grand_gross_profit,
            format3_colored_right
        )

        sheet.write(
            row,
            22,
            grand_tax_amount,
            format3_colored_right
        )

        sheet.write(
            row,
            24,
            grand_commission_income,
            format3_colored_right
        )

        sheet.write(
            row,
            25,
            grand_vendor_basis,
            format3_colored_right
        )