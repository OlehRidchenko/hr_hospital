from odoo import models, fields


class Patient(models.Model):
    _name = "hr_hospital.patient"
    _description = "Patient"

    name = fields.Char(string="Full Name", required=True)
    birth_date = fields.Date(string="Birth Date")
    doctor_id = fields.Many2one('hr_hospital.doctor', string="Doctor")
