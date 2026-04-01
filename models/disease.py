from odoo import models, fields


class Disease(models.Model):
    _name = "hr_hospital.disease"
    _description = "Disease"

    name = fields.Char(string="Disease Name", required=True)
    description = fields.Text(string="Description")
