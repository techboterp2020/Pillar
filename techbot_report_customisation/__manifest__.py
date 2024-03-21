# -*- coding: utf-8 -*-
{
    'name': 'Reports Customisation',
    'version': '16.0.1.1.0',
    'category': 'Reports',
    'summary': """Reports for Proforma and Invoice""",
    'author': 'Techbot Information Technology LLC',
    'depends': ['sale_management'],
    'data': [
        'reports/reports.xml',
        'reports/proforma_template.xml',
        'reports/invoice_template.xml',
        'views/res_company_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
