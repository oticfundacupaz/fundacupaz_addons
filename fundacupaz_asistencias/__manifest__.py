# -*- coding: utf-8 -*-
{
    'name': 'Fundacupaz Asistencias',
    'summary': 'Módulo para registrar asistencias de entrada importadas desde CSV biométrico.',
    'description': """
        Permite importar archivos CSV exportados desde lectores biométricos.
        - Lee las columnas CardNo (cédula), Date (fecha) y Time (hora).
        - Solo importa registros de tipo IN (entrada).
        - Busca automáticamente el nombre del contacto en res.partner por cédula.
        - Muestra los registros organizados en una vista de lista y formulario.
    """,
    'author': 'Fundacupaz',
    'website': '',
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail', 'hr', 'custom_empleados'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_csv_wizard_views.xml',
        'wizard/reporte_asistencia_wizard_views.xml',
        'report/reporte_asistencia.xml',
        'views/asistencia_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
