{
    'name': 'MIJ CANTV requerimientos',
    'version': '1.0',
    'description': "Requerimientos del Ministerio Interior Justicia y Paz con CANTV",
    'depends': ['base', 'web', 'mail', 'l10n_ve_dpt-10'],
    'data': [
        'views/mijcantv_requerimiento.xml',
        'views/mijcantv_entes.xml',
        # 'reportes/fundacupaz_reportes_entrega.xml',
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
