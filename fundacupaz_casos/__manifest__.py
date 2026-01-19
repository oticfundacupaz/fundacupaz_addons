{
    'name': 'Fundacupaz: Gestión de Casos',
    'version': '1.0',
    'category': 'Operations',
    'summary': 'Remisiones y Cancelaciones de Líneas Telefónicas',
    'description': """
        Módulo satélite para gestionar casos de telefonía:
        - Remisiones (Cambio de responsable/ente).
        - Cancelaciones (Baja de línea).
        Impacta automáticamente el inventario en fundacupaz_phone.
    """,
    'depends': ['base', 'mail', 'fundacupaz_phone'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/fundacupaz_caso_views.xml',
        'views/fundacupaz_menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}