# -*- coding: utf-8 -*-
{
    "name": "CNO Baked Report",

    'version': '19.0.0.0',

    'summary': """CNO Baked Report""",

    'description': """CNO Baked Report""",

    'category': 'Baked',

    'author': "Cyngro",

    'website': 'https://cyngro.com',

    "depends": ['base','report_xlsx','cno_baked_custom'],

    "data": [
        'security/ir.model.access.csv',
        'report/report_action.xml',
        'report/expenses_voucher_report_template.xml',
        'wizards/sale_analysis_report_wizard.xml',
        'wizards/quant_report_wizard_view.xml',
        'wizards/stock_move_analytic_report_wizard_views.xml',
        'wizards/expense_voucher_report_wizard_view.xml',
    ],




    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}
