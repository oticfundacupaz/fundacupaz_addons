{
    'name': 'Fundacupaz Hoja de Ruta',
    'version': '1.0',
    'summary': 'Módulo personalizado para el seguimiento de hojas de ruta',
    'description': """
        Este módulo permite gestionar y hacer seguimiento del avance de las hojas de ruta
        con diferentes vistas (Formulario, Lista, Kanban, Pivot, Calendario, Gráfico, Búsqueda)
        y un sistema de estatus y porcentaje de progreso.
    """,
    'author': 'Fundacupaz',
    'website': 'Tu Sitio Web (opcional)',
    'category': 'Project Management',
    'depends': ['base','mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/hoja_de_ruta_views.xml',
        'views/hoja_de_ruta_linea_views.xml',  # Vistas de la Línea de Seguimiento
        'views/hoja_de_ruta_paso_base_views.xml',  # Nuevas vistas para pasos base
        'data/hoja_de_ruta_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}