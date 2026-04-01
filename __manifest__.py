{
    'name': 'HR Hospital',
    'version': '17.0.1.0.0',
    'author': 'Dev',
    'category': 'Healthcare',
    'license': 'OPL-1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'data/disease_data.xml',
        'views/doctor_views.xml',
        'views/patient_views.xml',
        'views/disease_views.xml',
        'views/visit_views.xml',
        'views/hr_hospital_menu.xml',
    ],
    'demo': [
        'data/doctor_demo.xml',
        'data/patient_demo.xml',
    ],

    'installable': True,
    'application': True
}
