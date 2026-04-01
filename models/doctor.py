from odoo import models, fields


class Doctor(models.Model):
    _name = "hr_hospital.doctor"
    _description = "Doctor"

    name = fields.Char(string="Full Name", required=True)
    specialization = fields.Char(string="Specialization")
