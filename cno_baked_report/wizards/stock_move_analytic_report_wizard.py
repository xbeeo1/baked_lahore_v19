import io
import base64
import logging
from datetime import datetime, time
from collections import defaultdict
import xlsxwriter

_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class StockMoveAnalyticReportWizard(models.TransientModel):
    _name = "stock.move.analytic.report.wizard"
    _description = "Stock Move Analytic Excel Report Wizard"

    date_from = fields.Date(string="From Date", required=True)
    date_to = fields.Date(string="To Date", required=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        domain="[('plan_id.is_pos_plan', '=', True)]",
    )

    def action_print_report(self):
        self.ensure_one()

        _logger.info("=== [ANALYTIC REPORT DEBUG] START ===")
        _logger.info("date_from=%s date_to=%s analytic_account_id=%s",
                     self.date_from, self.date_to, self.analytic_account_id)

        if self.analytic_account_id:
            accounts = self.analytic_account_id
        else:
            accounts = self.env["account.analytic.account"].with_context(
                active_test=False
            ).search([("plan_id.is_pos_plan", "=", True)])

        _logger.info("Accounts fetched (%s): %s", len(accounts),
                     [(a.id, a.name) for a in accounts])

        # --- Make date_to inclusive of the whole day (Datetime vs Date mismatch fix) ---
        date_from = self.date_from
        date_to = self.date_to
        if date_to and not isinstance(date_to, datetime):
            date_to = datetime.combine(date_to, time(23, 59, 59))
        if date_from and not isinstance(date_from, datetime):
            date_from = datetime.combine(date_from, time(0, 0, 0))

        _logger.info("Normalized date_from=%s date_to=%s", date_from, date_to)

        # Filter by the creation date of the related scrap order, not by
        # expiry_date on the move itself.
        scraps = self.env["stock.scrap"].search([
            ("create_date", ">=", date_from),
            ("create_date", "<=", date_to),
        ])
        move_ids = scraps.mapped("move_ids").ids

        domain = [
            ("id", "in", move_ids),
            ("state", "=", "done"),
            ("analytic_distribution", "!=", False),
        ]
        _logger.info("Stock move search domain (filtered by scrap create_date): %s", domain)

        moves = self.env["stock.move"].search(domain)

        _logger.info("Moves found: %s", len(moves))
        for m in moves:
            _logger.info(
                "Move id=%s expiry_date=%s state=%s product=%s analytic_distribution=%s",
                m.id, m.expiry_date, m.state, m.product_id.display_name, m.analytic_distribution
            )

        if not moves:
            _logger.warning(
                "No stock moves matched the domain at all — check date range/state/"
                "analytic_distribution presence before looking at per-account matching."
            )

        # ------------------------------------------------------------------
        # Build a data structure: for each account -> for each product ->
        # aggregated {vendor, qty, returned, loss}
        # Also build a global ordered list of (product_id, product, vendor)
        # so every account uses the same row order.
        # ------------------------------------------------------------------
        account_product_data = {}  # {account_id: {product_id: {"qty":.., "returned":.., "loss":.., "vendor":..}}}
        product_info = {}  # {product_id: {"display_name":.., "vendor":..}}
        product_order = []  # keeps first-seen order

        for account in accounts:
            account_id_str = str(account.id)
            _logger.info(
                "--- Matching moves for account: %s (id=%s / id_str=%r) ---",
                account.name, account.id, account_id_str
            )

            product_data = defaultdict(lambda: {"qty": 0.0, "returned": 0.0, "loss": 0.0, "vendor": ""})

            for move in moves:
                if not move.analytic_distribution:
                    continue

                for key, percentage in move.analytic_distribution.items():
                    account_ids_in_key = [k.strip() for k in key.split(",")]
                    if account_id_str not in account_ids_in_key:
                        _logger.info(
                            "  NO MATCH: move %s key %r did not contain account_id %r",
                            move.id, key, account_id_str
                        )
                        continue

                    _logger.info(
                        "  MATCH: move %s matched account %s via key %r (pct=%s)",
                        move.id, account.id, key, percentage
                    )

                    product = move.product_id
                    vendor = product.seller_ids[:1].partner_id.name if product.seller_ids else ""
                    ratio = percentage / 100.0
                    qty = move.Qty * ratio

                    list_price = product.list_price
                    expiration_per = (product.expiration_per or 0.0) / 100.0
                    loss_amount = qty * expiration_per * list_price
                    returned_amount = qty * (1 - expiration_per) * list_price

                    pid = product.id
                    if pid not in product_info:
                        product_info[pid] = {
                            "display_name": product.display_name,
                            "vendor": vendor,
                        }
                        product_order.append(pid)

                    product_data[pid]["qty"] += qty
                    product_data[pid]["returned"] += returned_amount
                    product_data[pid]["loss"] += loss_amount
                    if vendor:
                        product_data[pid]["vendor"] = vendor

                    _logger.info(
                        "  Accumulated for account=%s product=%s: qty=%s returned=%s loss=%s",
                        account.name, product.display_name,
                        product_data[pid]["qty"], product_data[pid]["returned"], product_data[pid]["loss"]
                    )
                    break  # move already counted for this account, go to next move

            if product_data:
                account_product_data[account.id] = product_data
                _logger.info(
                    "Account %s (%s): %s distinct products matched",
                    account.name, account.id, len(product_data)
                )
            else:
                _logger.info(
                    "Account %s (%s) has NO matched data — excluding it from the report",
                    account.name, account.id
                )

        # Only keep accounts that actually had matched data, so empty
        # accounts (e.g. Cantt with 0 moves) do not get a column block.
        accounts_with_data = accounts.filtered(lambda a: a.id in account_product_data)

        _logger.info("Accounts with data (%s): %s", len(accounts_with_data),
                     [(a.id, a.name) for a in accounts_with_data])

        _logger.info("Global product order (%s products): %s",
                     len(product_order), [product_info[p]["display_name"] for p in product_order])

        # ------------------------------------------------------------------
        # Build a single worksheet:
        # Col 0 = Item Name, Col 1 = Vendor Name
        # Then for each account WITH DATA: 3 columns (Qty, Returned Amount, Loss Amount)
        # Row 0: date title
        # Row 1-2: merged headers ("Item Name"/"Vendor Name" span 2 rows,
        #          account name spans 3 cols on row1, sub-headers on row2)
        # Row 3+: data
        # ------------------------------------------------------------------
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        header_fmt = workbook.add_format({
            "bold": True, "bg_color": "#595959", "font_color": "white",
            "border": 1, "align": "center", "valign": "vcenter",
        })
        cell_fmt = workbook.add_format({"border": 1})
        title_fmt = workbook.add_format({"bold": True, "font_size": 12})

        sheet = workbook.add_worksheet("Product Expiry Report")

        sheet.write(0, 0, datetime.today().strftime("%d-%b-%Y"), title_fmt)

        sheet.merge_range(1, 0, 2, 0, "Item Name", header_fmt)
        sheet.merge_range(1, 1, 2, 1, "Vendor Name", header_fmt)

        sheet.set_column(0, 0, 40)
        sheet.set_column(1, 1, 25)

        col = 2
        account_col_start = {}  # {account_id: starting column index}
        for account in accounts_with_data:
            start = col
            end = col + 2
            sheet.merge_range(1, start, 1, end, account.name, header_fmt)
            sheet.write(2, start, "Qty", header_fmt)
            sheet.write(2, start + 1, "Returned Amount", header_fmt)
            sheet.write(2, start + 2, "Loss Amount", header_fmt)
            sheet.set_column(start, end, 15)
            account_col_start[account.id] = start
            col = end + 1

        # --- Aggregated totals block (sum across all analytic accounts) ---
        total_col_start = col
        sheet.merge_range(1, total_col_start, 1, total_col_start + 2, "Aggregated", header_fmt)
        sheet.write(2, total_col_start, "Total Qty", header_fmt)
        sheet.write(2, total_col_start + 1, "Total Returned Amt", header_fmt)
        sheet.write(2, total_col_start + 2, "Total Loss Amt", header_fmt)
        sheet.set_column(total_col_start, total_col_start + 2, 18)

        _logger.info("Account column start positions: %s", account_col_start)
        _logger.info("Total (aggregated) column start position: %s", total_col_start)

        row = 3
        for pid in product_order:
            info = product_info[pid]
            sheet.write(row, 0, info["display_name"], cell_fmt)
            sheet.write(row, 1, info["vendor"], cell_fmt)

            total_qty = 0.0
            total_returned = 0.0
            total_loss = 0.0

            for account in accounts_with_data:
                start = account_col_start[account.id]
                data = account_product_data[account.id].get(pid)
                if data:
                    sheet.write(row, start, data["qty"], cell_fmt)
                    sheet.write(row, start + 1, data["returned"], cell_fmt)
                    sheet.write(row, start + 2, data["loss"], cell_fmt)
                    total_qty += data["qty"]
                    total_returned += data["returned"]
                    total_loss += data["loss"]
                else:
                    sheet.write(row, start, "", cell_fmt)
                    sheet.write(row, start + 1, "", cell_fmt)
                    sheet.write(row, start + 2, "", cell_fmt)

            sheet.write(row, total_col_start, total_qty, cell_fmt)
            sheet.write(row, total_col_start + 1, total_returned, cell_fmt)
            sheet.write(row, total_col_start + 2, total_loss, cell_fmt)

            row += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env["ir.attachment"].create({
            "name": "Product_Expiry_Report.xlsx",
            "type": "binary",
            "datas": file_data,
            "res_model": self._name,
            "res_id": self.id,
        })

        _logger.info("=== [ANALYTIC REPORT DEBUG] END, attachment id=%s ===", attachment.id)

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }