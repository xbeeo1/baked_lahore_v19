# -*- coding: utf-8 -*-

from odoo import models

class ReportMrpMoOverview(models.AbstractModel):
    _inherit = 'report.mrp.report_mo_overview'

    def _format_component_move(
        self, production, move_raw, replenishments,
        replenish_data, level, index
    ):
        res = super()._format_component_move(
            production,
            move_raw,
            replenishments,
            replenish_data,
            level,
            index,
        )

        res['uom_precision'] = 8
        return res