# -*- coding: utf-8 -*-
{
    'name': 'Reports Customisation',
    'version': '16.0.2.1.0',
    'category': 'Reports',
    'summary': """Reports for Proforma and Invoice""",
    'author': 'Techbot Information Technology LLC',
    'depends': ['sale_management','account'],
    'data': [
        'reports/external_layout.xml',
        'views/res_partner_bank.xml',
        'reports/reports.xml',
        'reports/proforma_template.xml',
        'reports/commercial_invoice.xml',
        'reports/report_deliveryslip_inherit.xml',
        'views/res_company_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/stock_picking_view.xml',
        'reports/payment_receipt_inherit.xml',
        # 'reports/invoice_inherit.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
