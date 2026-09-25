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
        # Pre-pass: for every matched line, resolve its analytic accounts
        # into {plan_id: "account name(s)"} and collect the global ordered
        # list of plans that actually appear (so we only add columns for
        # plans that have data).
        # ------------------------------------------------------------------
        AnalyticAccount = self.env["account.analytic.account"]
        plan_order = []          # ordered list of plan ids that appear
        plan_names = {}          # {plan_id: plan display name}
        line_plan_values = {}    # {line.id: {plan_id: "account names"}}

        for entry in report_rows:
            for line in entry["lines"]:
                plan_dict = {}
                if line.analytic_distribution:
                    for key in line.analytic_distribution.keys():
                        acc_ids = [int(k) for k in key.split(",")]
                        accounts = AnalyticAccount.browse(acc_ids)
                        for acc in accounts:
                            plan = acc.plan_id
                            if not plan:
                                continue
                            if plan.id not in plan_order:
                                plan_order.append(plan.id)
                                plan_names[plan.id] = plan.name
                            plan_dict.setdefault(plan.id, [])
                            if acc.name not in plan_dict[plan.id]:
                                plan_dict[plan.id].append(acc.name)
                line_plan_values[line.id] = {
                    pid: ", ".join(names) for pid, names in plan_dict.items()
                }

        _logger.info("Analytic plans appearing in report (%s): %s",
                     len(plan_order), [plan_names[p] for p in plan_order])

        # ------------------------------------------------------------------
        # Build Excel: left block = voucher header fields (merged across the
        # voucher's line rows), right block = one row per line.
        # "Analytic Distribution" is a grouped header spanning one
        # sub-column per analytic plan that appears in the data.
        # ------------------------------------------------------------------
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#595959", "font_color": "white",
            "border": 1, "align": "center", "valign": "vcenter",
        })
        cell_fmt = workbook.add_format({"border": 1, "valign": "vcenter"})
        cell_center_fmt = workbook.add_format({"border": 1, "valign": "vcenter", "align": "center"})
        title_fmt = workbook.add_format({"bold": True, "font_size": 12})

        # Amount formats: comma-separated (e.g. 1,000)
        amount_fmt = workbook.add_format({"border": 1, "valign": "vcenter", "num_format": "#,##0.00"})
        subtotal_label_fmt = workbook.add_format({
            "bold": True, "border": 1, "valign": "vcenter", "align": "right",
            "bg_color": "#D9D9D9",
        })
        subtotal_amount_fmt = workbook.add_format({
            "bold": True, "border": 1, "valign": "vcenter", "bg_color": "#D9D9D9",
            "num_format": "#,##0.00",
        })
        grandtotal_label_fmt = workbook.add_format({
            "bold": True, "font_size": 11, "border": 2, "valign": "vcenter", "align": "right",
            "bg_color": "#595959", "font_color": "white",
        })
        grandtotal_amount_fmt = workbook.add_format({
            "bold": True, "font_size": 11, "border": 2, "valign": "vcenter",
            "bg_color": "#595959", "font_color": "white", "num_format": "#,##0.00",
        })

        sheet = workbook.add_worksheet("Expenses Voucher Report")

        sheet.write(0, 0, datetime.today().strftime("%d-%b-%Y"), title_fmt)

        # --- Fixed left/right headers, merged across the 2 header rows ---
        fixed_headers_before = ["Date", "Voucher #", "MOP", "Payee", "State",
                                 "Accounting Head", "Account"]
        fixed_headers_after = ["Description", "Amount"]

        col = 0
        for label in fixed_headers_before:
            sheet.merge_range(1, col, 2, col, label, header_fmt)
            col += 1

        # --- "Analytic Distribution" grouped header + one sub-column per plan ---
        analytic_start_col = col
        analytic_end_col = col + max(len(plan_order), 1) - 1
        if plan_order:
            sheet.merge_range(1, analytic_start_col, 1, analytic_end_col,
                               "Analytic Distribution", header_fmt)
            plan_col_index = {}
            for plan_id in plan_order:
                sheet.write(2, col, plan_names[plan_id], header_fmt)
                plan_col_index[plan_id] = col
                col += 1
        else:
            # No analytic data at all - still show an empty grouped header
            sheet.merge_range(1, analytic_start_col, 1, analytic_end_col,
                               "Analytic Distribution", header_fmt)
            sheet.write(2, analytic_start_col, "", header_fmt)
            plan_col_index = {}
            col += 1

        after_start_col = col
        for label in fixed_headers_after:
            sheet.merge_range(1, col, 2, col, label, header_fmt)
            col += 1

        # Column widths
        sheet.set_column(0, 0, 14)   # Date
        sheet.set_column(1, 1, 15)   # Voucher #
        sheet.set_column(2, 2, 15)   # MOP
        sheet.set_column(3, 3, 20)   # Payee
        sheet.set_column(4, 4, 20)   # State
        sheet.set_column(5, 5, 20)   # Accounting Head
        sheet.set_column(6, 6, 25)   # Account
        sheet.set_column(analytic_start_col, analytic_end_col, 20)  # analytic plan columns
        sheet.set_column(after_start_col, after_start_col, 25)      # Description
        sheet.set_column(after_start_col + 1, after_start_col + 1, 15)  # Amount

        description_col = after_start_col
        amount_col = after_start_col + 1
        total_cols_span = amount_col - 1  # last col before Amount, for merged "Total"/"Grand Total" labels

        row = 3
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
                sheet.write(row, 5, line.accounting_head_id.name or "", cell_fmt)
                sheet.write(row, 6, line.account_id.display_name or "", cell_fmt)

                plan_values = line_plan_values.get(line.id, {})
                for plan_id, pcol in plan_col_index.items():
                    sheet.write(row, pcol, plan_values.get(plan_id, ""), cell_fmt)

                sheet.write(row, description_col, line.description or "", cell_fmt)
                sheet.write_number(row, amount_col, line.amount, amount_fmt)

                voucher_total += line.amount
                row += 1

            grand_total += voucher_total

            # --- Voucher subtotal row ---
            sheet.merge_range(row, 0, row, total_cols_span, "Total", subtotal_label_fmt)
            sheet.write_number(row, amount_col, voucher_total, subtotal_amount_fmt)
            row += 1

        # --- Grand total row ---
        sheet.merge_range(row, 0, row, total_cols_span, "Grand Total", grandtotal_label_fmt)
        sheet.write_number(row, amount_col, grand_total, grandtotal_amount_fmt)

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