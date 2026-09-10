# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError
from collections import defaultdict
from datetime import datetime , time , timedelta
from pytz import timezone, UTC
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from collections import defaultdict


class SaleAnalysisReport(models.TransientModel):
    _name = "sale.analysis.report"

    date_from = fields.Datetime(string='Date From', required= True)
    date_to = fields.Datetime(string='Date To', required= True)




    def action_print(self):
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('cno_baked_report.sale_analysis_report_xlsx_details').report_action(self, data=data)


