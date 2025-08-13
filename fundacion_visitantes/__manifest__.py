{
    'name': "Registro de Visitantes",
    'summary': "Un módulo de registro de visitantes con una interfaz similar al módulo de Inventario.",
    'description': """
        Permite a la recepción registrar la información de los visitantes.
        - Hoja de registro para el control de las visitas diarias.
        - Campos para el registro de la información del visitante, motivo, y destino.
        - Creación automática de visitantes si no existen.
        - Historial de todas las visitas para futuras consultas.
    """,
    'author': "Tu Nombre",
    'website': "http://www.tuempresa.com",
    'category': 'Extra Tools',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/visitante_views.xml',
        'views/visita_hoja_views.xml',
],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}