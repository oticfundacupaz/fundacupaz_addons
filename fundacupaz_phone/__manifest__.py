{
    'name': 'Fundacupaz Phone',
    'version': '1.0',
    'description': "inventario de telefonos de fundacupaz",
    'depends': ['base','purchase', 'web', 'mail', 'fleet', 'hr', 'stock', 'l10n_ve_dpt-10', 'project', 'contacts', 'event'],
    # Contenido de fundacupaz_phone/__manifest__.py (Bloque 'data')

    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'data/fundacupaz_sequence.xml',
    'wizards/registrar_ocurrencia_wizard_views.xml',
    'views/fundacupaz_phone_plan_views.xml',
    'views/fundacupaz_cuadrantes_views.xml',

    # 1. DEFINE EL ID: action_report_ocurrencia
    'reports/report_ocurrencia_cuadrante_template.xml',

    # 2. USA EL ID: %(fundacupaz_phone.action_report_ocurrencia)d
    'views/fundacupaz_ocurrencia_views.xml',

    'views/fundacupaz_pc_views.xml',
    'wizards/report_verificacion_wizard_views.xml',
    'views/comisionado_estadal.xml',
    'views/fundacupaz_views.xml',
    'views/fundacupaz_moto_views.xml',
    'views/fundacupaz_fleet_views.xml',
    'views/fundacupaz_entes_views.xml',
],

    'installable': True,
    'license': 'LGPL-3',
    # 'assets': {
    #     'web.assets_backend': [
    #         'fundacupaz_phone/static/src/**/*',
    #     ],
    # },
}
