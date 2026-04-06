{
    'name': 'HR Hospital',
    'version': '17.0.1.0.0',
    'author': 'Dev',
    'category': 'Healthcare',
    'license': 'OPL-1',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',

        'views/doctor_views.xml',
        'views/patient_views.xml',
        'views/disease_views.xml',
        'views/visit_views.xml',
        'views/wizard_views.xml',

        'wizards/mass_reassign_doctor_wizard_views.xml',
        'wizards/disease_report_wizard_views.xml',
        'wizards/reschedule_visit_wizard_views.xml',
        'wizards/doctor_schedule_wizard_views.xml',
        'wizards/patient_card_export_wizard_views.xml',

        'views/hr_hospital_menu.xml',
    ],
    'demo': [
        'demo/speciality_data.xml',
        'demo/doctor_data.xml',
        'demo/contact_person_data.xml',
        'demo/patient_data.xml',
        'demo/disease_data.xml',
        'demo/schedule_data.xml',
        'demo/visit_data.xml',
        'demo/diagnosis_data.xml',
        'demo/history_data.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
}