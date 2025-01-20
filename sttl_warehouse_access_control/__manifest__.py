# Manifest file of warehouse_access_control
{
    'name': 'Warehouse Access Management',
    'version' : '18.0.1.0',
    'depends': ['base', 'stock'],
    'description': '''
       Warehouse Access Control
   ''',
    'data':[         
      'views/res_users_views.xml',
      'security/warehouse_group.xml',
      'security/warehouse_security.xml',      
    ],
    'images': ['static/description/banner.png'],
    'category': 'Warehouse',
    "author": "Silver Touch Technologies Limited",
    'installable': True,
    'application': False,
}
