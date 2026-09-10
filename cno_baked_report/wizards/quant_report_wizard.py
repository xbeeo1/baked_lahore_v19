import io
import base64
import xlsxwriter
from odoo import fields, models


class QuantReportWizard(models.TransientModel):
    _name = 'quant.report.wizard'
    _description = 'Stock Quant Report Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    def action_print_report(self):
        self.ensure_one()

        quants = self.env['stock.quant'].search([
            ('in_date', '>=', self.date_from),
            ('in_date', '<=', self.date_to),
            ('location_id.usage', 'in', ['internal', 'transit']),
        ])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Physical Inventory Adjustment Report')

        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
        cell_format = workbook.add_format({'border': 1})
        amount_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})

        headers = [
            'Vendor', 'Product', 'Last Move Date', 'Last Move Quantity',
            'Last Move By', 'Cost Price', 'Scheduled',
            'On Hand', 'Counted', 'Difference', 'Adjustment Cost',
        ]
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        row = 1
        for quant in quants:
            sheet.write(row, 0, quant.vendor_id.name or '', cell_format)
            sheet.write(row, 1, quant.product_id.display_name or '', cell_format)
            sheet.write(row, 2, str(quant.last_move_date or ''), cell_format)
            sheet.write(row, 3, quant.last_move_quantity, cell_format)
            sheet.write(row, 4, quant.last_move_user_id.name or '', cell_format)
            sheet.write_number(row, 5, quant.cost_price, amount_format)
            sheet.write(row, 6, str(quant.in_date or ''), cell_format)
            sheet.write(row, 7, quant.quantity, cell_format)
            sheet.write(row, 8, quant.inventory_quantity, cell_format)
            sheet.write(row, 9, quant.inventory_diff_quantity, cell_format)
            sheet.write_number(row, 10, quant.adjustment_cost, amount_format)
            row += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Physical_Inventory_Adjustment_Report.xlsx',
            'type': 'binary',
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }