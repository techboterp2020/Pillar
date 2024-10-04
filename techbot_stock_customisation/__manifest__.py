# -*- coding: utf-8 -*-
{
    'name': 'Stock Customisation',
    'version': '16.0.1.1.0',
    'category': 'Stock',
    'summary': """The Vehicle Integration module for Odoo revolutionizes inventory management by seamlessly incorporating essential vehicle details into stock move lines, lots, and serial number models. 
    Now, you can effortlessly track and manage your inventory with the added granularity of vehicle information,
     providing a comprehensive overview of stock movements.""",
    'author': 'Techbot Information Technology LLC',
    'depends': ['base', 'stock', ],
    'data': [
        'views/stock_move_line.xml',
        'views/stock_lot.xml',
        'views/stock_quant.xml',
        'views/product.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}
