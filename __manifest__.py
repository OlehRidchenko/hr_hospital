{
    'name': 'HR Hospital',
    'version': '17.0.1.0.0',
    'author': 'Dev',
    'category': 'Healthcare',
    'license': 'OPL-1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',

        'data/speciality_data.xml',
        'data/doctor_data.xml',
        'data/contact_person_data.xml',
        'data/patient_data.xml',
        'data/disease_data.xml',
        'data/schedule_data.xml',
        'data/visit_data.xml',
        'data/diagnosis_data.xml',
        'data/history_data.xml',

        'wizards/mass_reassign_doctor_wizard_views.xml',
        'wizards/disease_report_wizard_views.xml',
        'wizards/reschedule_visit_wizard_views.xml',
        'wizards/doctor_schedule_wizard_views.xml',
        'wizards/patient_card_export_wizard_views.xml',

        'views/doctor_views.xml',
        'views/patient_views.xml',
        'views/disease_views.xml',
        'views/visit_views.xml',
        'views/additional_views.xml',
        'views/hr_hospital_menu.xml',
    ],

    'demo': [
    ],

    'assets': {},
    'installable': True,
    'application': True
}
