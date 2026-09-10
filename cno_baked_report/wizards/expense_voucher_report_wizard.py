# -*- coding: utf-8 -*-

import io
import base64
import logging
from datetime import datetime

import xlsxwriter

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ExpensesVoucherReportWizard(models.TransientModel):
    _name = "expenses.voucher.report.wizard"
    _description = "Expenses Voucher Excel Report Wizard"

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        string="Analytic Accounts",
    )

    def action_print_report(self):
        self.ensure_one()

        _logger.info("=== [EXPENSES VOUCHER REPORT] START ===")
        _logger.info("date_from=%s date_to=%s analytic_account_ids=%s",
                     self.date_from, self.date_to, self.analytic_account_ids.ids)

        domain = [
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]
        vouchers = self.env["expenses.voucher"].search(domain, order="date, voucher_no")

        _logger.info("Vouchers found (before analytic filter): %s", len(vouchers))

        selected_account_ids = set(self.analytic_account_ids.ids)

        report_rows = []

        for voucher in vouchers:
            if selected_account_ids:
                matched_lines = voucher.expenses_voucher_line.filtered(
                    lambda l: l.analytic_distribution and any(
                        str(acc_id) in [k.strip() for k in key.split(",")]
                        for key in l.analytic_distribution.keys()
                        for acc_id in selected_account_ids
                    )
                )
                _logger.info(
                    "Voucher %s: %s/%s lines matched selected analytic accounts",
                    voucher.voucher_no, len(matched_lines), len(voucher.expenses_voucher_line)
                )
            else:
                matched_lines = voucher.expenses_voucher_line
                _logger.info(
                    "Voucher %s: no analytic filter applied, keeping all %s lines",
                    voucher.voucher_no, len(matched_lines)
                )

            if matched_lines:
                report_rows.append({"voucher": voucher, "lines": matched_lines})

        _logger.info("Vouchers included in report (after analytic filter): %s", len(report_rows))

        # ------------------------------------------------------------------
        # Build Excel: left block = voucher header fields (merged across the
        # voucher's line rows), right block = one row per line.
        # ------------------------------------------------------------------
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#4472C4", "font_color": "white",
            "border": 1, "align": "center", "valign": "vcenter",
        })
        cell_fmt = workbook.add_format({"border": 1, "valign": "vcenter"})
        cell_center_fmt = workbook.add_format({"border": 1, "valign": "vcenter", "align": "center"})
        title_fmt = workbook.add_format({"bold": True, "font_size": 12})

        # Amount formats: comma-separated (e.g. 1,000)
        amount_fmt = workbook.add_format({"border": 1, "valign": "vcenter", "num_format": "#,##0.00"})
        subtotal_label_fmt = workbook.add_format({
            "bold": True, "border": 1, "valign": "vcenter", "align": "right",
            "bg_color": "#D9E1F2",
        })
        subtotal_amount_fmt = workbook.add_format({
            "bold": True, "border": 1, "valign": "vcenter", "bg_color": "#D9E1F2",
            "num_format": "#,##0.00",
        })
        grandtotal_label_fmt = workbook.add_format({
            "bold": True, "font_size": 11, "border": 2, "valign": "vcenter", "align": "right",
            "bg_color": "#4472C4", "font_color": "white",
        })
        grandtotal_amount_fmt = workbook.add_format({
            "bold": True, "font_size": 11, "border": 2, "valign": "vcenter",
            "bg_color": "#4472C4", "font_color": "white", "num_format": "#,##0.00",
        })

        sheet = workbook.add_worksheet("Expenses Voucher Report")

        sheet.write(0, 0, datetime.today().strftime("%d-%b-%Y"), title_fmt)

        headers = [
            "Date", "Voucher #", "MOP", "Payee", 'State',
            "Accounting Head", "Account", "Analytic Distribution",
            "Description", "Amount",
        ]
        for col_idx, label in enumerate(headers):
            sheet.write(1, col_idx, label, header_fmt)

        sheet.set_column(0, 0, 14)   # Date
        sheet.set_column(1, 1, 15)   # Voucher #
        sheet.set_column(2, 2, 15)   # MOP
        sheet.set_column(3, 3, 20)   # Payee
        sheet.set_column(4, 4, 20)   # state
        sheet.set_column(5, 5, 20)   # Accounting Head
        sheet.set_column(6, 6, 25)   # Account
        sheet.set_column(7, 7, 22)   # Analytic Distribution
        sheet.set_column(8, 8, 25)   # Description
        sheet.set_column(9, 9, 15)   # Amount

        row = 2
        grand_total = 0.0

        for entry in report_rows:
            voucher = entry["voucher"]
            lines = entry["lines"]
            n_lines = len(lines)
            start_row = row
            end_row = row + n_lines - 1

            _logger.info(
                "Writing voucher %s: rows %s-%s (%s lines)",
                voucher.voucher_no, start_row, end_row, n_lines
            )

            # --- Left block: voucher header fields, merged vertically ---
            voucher_field_values = [
                (voucher.date.strftime("%d-%b-%Y") if voucher.date else ""),
                voucher.voucher_no or "",
                voucher.mop_id.name or "",
                voucher.payee_id.name or "",
                voucher.state or "",
            ]

            for col_idx, value in enumerate(voucher_field_values):
                if n_lines > 1:
                    sheet.merge_range(start_row, col_idx, end_row, col_idx, value, cell_center_fmt)
                else:
                    sheet.write(start_row, col_idx, value, cell_center_fmt)

            # --- Right block: one row per line ---
            voucher_total = 0.0
            for line in lines:
                analytic_names = ", ".join(
                    self.env["account.analytic.account"].browse(
                        [int(k) for key in line.analytic_distribution.keys()
                         for k in key.split(",")]
                    ).mapped("name")
                ) if line.analytic_distribution else ""

                sheet.write(row, 5, line.accounting_head_id.name or "", cell_fmt)
                sheet.write(row, 6, line.account_id.display_name or "", cell_fmt)
                sheet.write(row, 7, analytic_names, cell_fmt)
                sheet.write(row, 8, line.description or "", cell_fmt)
                sheet.write_number(row, 9, line.amount, amount_fmt)

                voucher_total += line.amount
                row += 1

            grand_total += voucher_total

            # --- Voucher subtotal row ---
            sheet.merge_range(row, 0, row, 8, "Total", subtotal_label_fmt)
            sheet.write_number(row, 9, voucher_total, subtotal_amount_fmt)
            row += 1

        # --- Grand total row ---
        sheet.merge_range(row, 0, row, 8, "Grand Total", grandtotal_label_fmt)
        sheet.write_number(row, 9, grand_total, grandtotal_amount_fmt)

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env["ir.attachment"].create({
            "name": "Expenses_Voucher_Report.xlsx",
            "type": "binary",
            "datas": file_data,
            "res_model": self._name,
            "res_id": self.id,
        })

        _logger.info("=== [EXPENSES VOUCHER REPORT] END, attachment id=%s ===", attachment.id)

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }