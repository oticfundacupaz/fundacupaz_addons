{
    'name': 'Reportes Fundacupaz Firma',
    'summary': 'Añade un pie de firma a los reportes de inventario de Fundacupaz.',
    'description': """
        Este módulo personaliza los reportes PDF de órdenes de entrega y recepción
        estándar de Odoo 18 para incluir un pie de firma de tres columnas
        solo en la última página, adaptado a los requerimientos de Fundacupaz.
    """,
    'author': 'Tu Nombre', # No olvides cambiar esto
    'website': 'https://www.fundacupaz.org', # Sugerencia: ajusta según sea necesario
    'category': 'Inventory/Reporting',
    'version': '1.0',
    'depends': ['stock'],
    'data': [
        'reports/stock_picking_templates.xml',
       # 'reports/stock_picking_styles.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}