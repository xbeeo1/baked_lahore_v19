# -*- coding: utf-8 -*-

from odoo import models, api


class PnlDashboard(models.Model):
    _name = 'pnl.dashboard'
    _description = 'P&L Dashboard Data Provider'

    @api.model
    def _get_pnl_report(self):
        """Locate the standard Profit and Loss report."""

        report = self.env.ref(
            'account_reports.profit_and_loss',
            raise_if_not_found=False
        )

        if not report:
            report = self.env['account.report'].search(
                [('name', 'ilike', 'profit and loss')],
                limit=1
            )

        if not report:
            report = self.env['account.report'].search(
                [('name', 'ilike', 'profit')],
                limit=1
            )

        return report

    @api.model
    def get_pos_analytic_accounts(self):
        """Return analytic accounts whose plan has is_pos_plan = True."""
        accounts = self.env['account.analytic.account'].search([
            ('plan_id.is_pos_plan', '=', True)
        ])
        return [{'id': a.id, 'name': a.name} for a in accounts]

    @api.model
    def get_pnl_data(
            self,
            date_from=None,
            date_to=None,
            company_id=None,
            analytic_account_id=None
    ):
        try:
            report = self._get_pnl_report()

            if not report:
                return {
                    'error': (
                        'Profit and Loss report not found. '
                        'Please check that the Accounting Reports '
                        'module is installed.'
                    ),
                    'lines': [],
                    'company': self.env.company.name,
                    'currency': self.env.company.currency_id.symbol,
                }

            company = (
                self.env['res.company'].browse(company_id)
                if company_id
                else self.env.company
            )

            if not company.exists():
                company = self.env.company

            options_context = {
                'date': {
                    'date_from': date_from,
                    'date_to': date_to,
                    'filter': 'custom',
                    'mode': 'range',
                },
            }

            options = report.get_options(options_context)

            if analytic_account_id:
                analytic_domain = [
                    ('analytic_distribution', 'in', [analytic_account_id])
                ]
                options['forced_domain'] = options.get('forced_domain', []) + analytic_domain

            selected_report_id = options.get('report_id')

            if selected_report_id:
                selected_report = self.env['account.report'].browse(
                    selected_report_id
                )

                if selected_report.exists():
                    report = selected_report

            lines = report._get_lines(options)

            result = []

            for line in lines:
                columns = []
                for col in line.get('columns', []):
                    columns.append({
                        'name': col.get('name'),
                        'no_format': col.get('no_format'),
                    })

                result.append({
                    'id': line.get('id'),
                    'name': line.get('name'),
                    'level': line.get('level', 0),
                    'columns': columns,
                    'is_total': 'total' in (line.get('class') or ''),
                    'unfoldable': line.get('unfoldable', False),
                })

            return {
                'lines': result,
                'company': company.name,
                'currency': company.currency_id.symbol,
            }
        except Exception as e:
            return {
                'error': str(e),
                'lines': [],
                'company': self.env.company.name,
                'currency': self.env.company.currency_id.symbol,
            }