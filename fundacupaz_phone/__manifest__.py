{
    'name': 'Fundacupaz Phone',
    'version': '1.0',
    'description': "inventario de telefonos de fundacupaz",
    'depends': ['base', 'web', 'mail', 'fleet', 'hr', 'stock', 'l10n_ve_dpt-10', 'project', 'contacts', 'event'],
    'data': [
        'views/fundacupaz_pc_views.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/comisionado_estadal.xml',
        'views/fundacupaz_views.xml',
        'views/fundacupaz_fleet_views.xml',
        'views/fundacupaz_entes_views.xml',
        'views/fundacupaz_inventario_views.xml',
        'reportes/fundacupaz_reportes_entrega.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
