{
    'name': 'Product Sync from MSSQL',
    'version': '1.0',
    'summary': 'Synchronize products from MSSQL to Odoo',
    'depends': ['product'],
    'data': [
        'data/product_cron.xml',
    ],
    'installable': True,
    'application': False,
}
