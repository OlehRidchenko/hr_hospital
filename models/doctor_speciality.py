from odoo import models, fields


class DoctorSpeciality(models.Model):
    _name = "doctor.speciality"
    _description = "Doctor Speciality"

    name = fields.Char(required=True)
    code = fields.Char(string="Speciality Code", size=10, required=True)
    description = fields.Text()
    active = fields.Boolean(string="Active", default=True)

    doctor_ids = fields.One2many(
        "hr_hospital.doctor",
        "speciality_id",
    )
