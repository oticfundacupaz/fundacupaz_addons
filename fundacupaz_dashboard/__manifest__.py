{
    'name': 'Fundacupaz Dashboard',
    'version': '1.0',
    'summary': 'Tablero para estadísticas de teléfonos',
    'description': """
        Un tablero para visualizar la cantidad de teléfonos por estatus y operadora.
    """,
    'author': 'Tu Nombre',
    'category': 'Extra Tools',
    'depends': ['base', 'web', 'fundacupaz_phone'],
    'data': [
        'security/ir.model.access.csv',
        'views/fundacupaz_dashboard_views.xml',
        'views/report_wizard_view.xml',
        'report/report_definition.xml',
        'report/report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}