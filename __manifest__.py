# -*- coding: utf-8 -*-
{
    'name': "EnzHotelManagment",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Managing the Hotel Industry.
""",

    'description': """
This module is for Managing the Hotel Industry.
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'account', 'stock', 'product', 'sale', 'sale_management', 'purchase', 'contacts', 'hr', 'hr_expense', 'sale_crm',
                'sale_project'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/hotel_configurations.xml',
        'views/sale_form.xml',
        'views/menus.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
