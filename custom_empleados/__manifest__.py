# -*- coding: utf-8 -*-

{
    'name': 'Custom Empleados',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Personaliza el formulario de empleados ocultando campos y pestañas no utilizados',
    'description': """
    Oculta los siguientes bloques de la vista de empleados:
    - Pestaña: Insignias recibidas
    - Información Privada: Permiso de trabajo
    - Ajustes: Asistencia/Punto de venta
    - Ajustes: Ajustes de la aplicación
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'hr',
        'hr_gamification'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/benefits_report_wizard_views.xml',
        'report/hr_employee_toy_report.xml',
        'report/hr_employee_toy_template.xml',
        'report/constancia_trabajo_report.xml',
        'report/constancia_trabajo_template.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
