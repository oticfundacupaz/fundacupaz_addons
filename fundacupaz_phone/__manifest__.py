{
    'name' : 'Fundacupaz Phone',
    'version': '1.0',
    'description': "inventario de telefonos de fundacupaz",
    'depends': ['base', 'web', 'mail', 'fleet' ,'stock', 'l10n_ve_dpt-10'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fundacupaz_views.xml',
        'views/fundacupaz_fleet_views.xml',
        'views/fundacupaz_entes_views.xml',
        'views/fundacupaz_inventario_views.xml',
        'reportes/fundacupaz_reportes_entrega.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
