# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ExpensesVoucher(models.Model):
    _name = "expenses.voucher"
    _description = "Expenses Voucher"
    _rec_name = "voucher_no"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']

    voucher_no = fields.Char(string="Voucher #",readonly=True,copy=False, default=lambda self: _('New EXPV'))
    expense_nature_id = fields.Many2one(comodel_name='expense.nature',string="Expense Nature")
    date = fields.Date(string="Date",default=fields.Date.today() , required=True)
    mop_id = fields.Many2one(comodel_name='account.journal',string="MOP",domain=[('type','in',['cash','bank'])] , required=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],default='draft',required=True)
    expenses_voucher_line = fields.One2many("expenses.voucher.line", "expenses_voucher_id",
                                           string="Expense Voucher Lines")
    payee_id = fields.Many2one(comodel_name='res.partner',string="Payee", required=True)
    move_id = fields.Many2one(comodel_name='account.move',string="Journal Entry")
    entry_total = fields.Integer(string="Expense Voucher", compute='_entry_total')
    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True,
    )

    @api.depends('expenses_voucher_line.amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.expenses_voucher_line.mapped('amount'))

    """COUNT ALL RELATED Journal Entry"""
    def _entry_total(self):
        for rec in self:
            invoice_count = self.env['account.move'].search_count([('expenses_voucher_id', '=', self.id), ('move_type', '=', 'entry')])
            rec.entry_total = invoice_count



    """VIEW RELATED Journal Entry"""

    def action_view_entry(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Journal Entry"),
            'view_mode': 'list,form',
            'domain': [('expenses_voucher_id', '=', self.id), ('move_type', '=', 'entry')],
        }
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('voucher_no', _('New EXPV')) == _('New EXPV'):
                vals['voucher_no'] = self.env['ir.sequence'].next_by_code(
                    'expenses.voucher'
                ) or _('New EXPV')

        return super().create(vals_list)

    def action_confirm(self):
        for move in self:
            attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', move.id),
            ])

            if not attachment_count:
                raise ValidationError(
                    _("Please attach at least one document before confirmation.")
                )

            misc_journal = self.env['account.journal'].search([('type', '=', 'general'),('name','=','Expense')], limit=1)
            lines = []
            if move.expenses_voucher_line:
                total_amount = 0
                for line in move.expenses_voucher_line:
                    analytic_distribution=line.analytic_distribution
                    lines.append((0, 0, {
                        'account_id': line.account_id.id,
                        'debit': line.amount,
                        'credit': 0.0,
                        'name': move.voucher_no,
                        'analytic_distribution': line.analytic_distribution,
                        'partner_id': move.payee_id.id,
                    }))
                    total_amount = total_amount + line.amount

                lines.append((0, 0, {
                    'account_id': move.mop_id.default_account_id.id,
                    'debit': 0.0,
                    'credit': total_amount,
                    'name':move.voucher_no,
                    'analytic_distribution':analytic_distribution,
                    'partner_id': move.payee_id.id,
                }))

            if lines:
                move_obj = self.env['account.move'].create({
                    'ref': move.voucher_no,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': lines,
                    'expenses_voucher_id':move.id,
                })
                move.move_id = move_obj.id
                move_obj.action_post()
        self.state = 'confirm'

    def action_cancel(self):
        for x in self:
            x.move_id.button_cancel()
        self.state = 'cancel'

    def action_reset_to_draft(self):
        self.state = 'draft'