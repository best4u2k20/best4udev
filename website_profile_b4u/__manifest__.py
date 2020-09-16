{
    'name': "Website Profile B4U",
    'version': '1.0.0',
    'author': 'B4U',
    'category': 'B4U',
    'website': 'https://www.best4ubuey.com',
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'depends': [
        'website_profile', 'auth_oauth', 'website_event', 'website_blog', 'website_sale', 'website_sale_wishlist'
    ],
    'summary': """
    Website Profile B4U
    """,
    'data': [
        'views/templates.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
