# -*- coding: utf-8 -*-
{
    'name': 'Medical Shop',
    'category': 'eCommerce',
    'summary': 'Medical Shop',
    'version': '1.0',
    'author': 'Kanak Info Systems',
    'description': """
Medical Shop
============
    """,
    'images': ['static/description/main_screenshot.png'],
    'depends': ['website_sale'],
    'data': [
        'data/data.xml',
        'views/shop_views.xml',
        'views/assets_templates.xml',
        'views/shop_templates.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'price': 0.0,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/AsOjMec3LYI',
}
