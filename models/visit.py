from odoo import models, fields


class Visit(models.Model):
    _name = "hr_hospital.visit"
    _description = "Patient Visit"

    patient_id = fields.Many2one('hr_hospital.patient',
                                 string="Patient", required=True)
    doctor_id = fields.Many2one('hr_hospital.doctor',
                                string="Doctor")
    disease_id = fields.Many2one('hr_hospital.disease',
                                 string="Disease")
    visit_date = fields.Datetime(string="Visit Date",
                                 default=fields.Datetime.now)
    notes = fields.Text(string="Notes")
