# -*- coding: utf-8 -*-

{
    "name": "CNO Baked Custom Dashboard",

    'version': '19.0.0.0',

    'summary': """CNO Baked Custom Dashboard""",

    'description': """CNO Baked Custom Dashboard""",

    'category': 'Dashboard',

    'author': "Musadiq Fiaz",

    'website': 'https://cyngro.com',

    "depends": ['base', 'point_of_sale', 'spreadsheet_dashboard', 'account_reports', 'web','cno_baked_custom','spreadsheet_dashboard_pos_hr'],

    "data": [
        'security/ir.model.access.csv',
        'views/pnl_dashboard_views.xml',
        'views/top_vendors_views.xml',
        'views/account_summary_views.xml',
        'data/pos_dashboard_vendor.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cno_baked_custom_dashboard/static/src/pnl_dashboard.js',
            'cno_baked_custom_dashboard/static/src/pnl_dashboard.xml',
            'cno_baked_custom_dashboard/static/src/pnl_dashboard.scss',
            'cno_baked_custom_dashboard/static/src/top_vendors.js',
            'cno_baked_custom_dashboard/static/src/top_vendors.xml',
            'cno_baked_custom_dashboard/static/src/top_vendors.scss',
            'cno_baked_custom_dashboard/static/src/account_summary_dashboard.js',
            'cno_baked_custom_dashboard/static/src/account_summary_dashboard.xml',
            'cno_baked_custom_dashboard/static/src/account_summary_dashboard.scss',
        ],
    },

}
