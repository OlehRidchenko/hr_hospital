from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Doctor(models.Model):
    _name = "hr_hospital.doctor"
    _description = "Doctor"
    _inherit = ["abstract.person"]

    user_id = fields.Many2one(
        "res.users",
        string="System User",
    )
    speciality_id = fields.Many2one(
        "doctor.speciality",
        string="Speciality",
    )
    is_intern = fields.Boolean(string="Intern")

    mentor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Mentor Doctor",
        domain=[("is_intern", "=", False)],
    )
    license_number = fields.Char(
        required=True,
        copy=False,
    )
    license_date = fields.Date(string="License Issue Date")

    experience_years = fields.Integer(
        string="Experience (years)",
        compute="_compute_experience",
        store=True,
    )
    rating = fields.Float(
        digits=(3, 2),
    )
    schedule_ids = fields.One2many(
        "doctor.schedule",
        "doctor_id",
        string="Work Schedule",
    )
    study_country_id = fields.Many2one(
        "res.country",
        string="Country of Study",
    )

    intern_ids = fields.One2many(
        "hr_hospital.doctor",
        "mentor_id",
        string="Interns",
        domain=[("is_intern", "=", True)],
    )

    _sql_constraints = [
        (
            "license_number_unique",
            "UNIQUE(license_number)",
            "License number must be unique!",
        ),
        (
            "rating_range",
            "CHECK(rating >= 0.0 AND rating <= 5.0)",
            "Rating must be between 0.00 and 5.00!",
        ),
    ]

    @api.depends("license_date")
    def _compute_experience(self):
        today = fields.Date.today()
        for rec in self:
            if rec.license_date:
                rec.experience_years = relativedelta(
                    today, rec.license_date
                ).years
            else:
                rec.experience_years = 0

    def name_get(self):
        result = []
        for rec in self:
            speciality = rec.speciality_id.name if rec.speciality_id else ""
            display = f"{rec.name} ({speciality})" if speciality else rec.name
            result.append((rec.id, display))
        return result

    @api.onchange("is_intern")
    def _onchange_is_intern(self):
        if not self.is_intern:
            self.mentor_id = False

    @api.onchange("is_intern", "mentor_id")
    def _onchange_fill_mentor(self):
        if self.is_intern and not self.mentor_id:
            mentor = self.env["hr_hospital.doctor"].search(
                [("is_intern", "=", False)],
                limit=1,
            )
            if mentor:
                self.mentor_id = mentor

    @api.constrains("rating")
    def _check_rating(self):
        for rec in self:
            if rec.rating < 0.0 or rec.rating > 5.0:
                raise ValidationError(
                    "Rating must be between 0.00 and 5.00!"
                )

    @api.constrains("is_intern", "mentor_id")
    def _check_intern_mentor(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.is_intern:
                raise ValidationError(
                    f"Doctor '{rec.mentor_id.name}' is an intern "
                    f"and cannot be assigned as a mentor!"
                )

    @api.constrains("mentor_id")
    def _check_self_mentor(self):
        for rec in self:
            if rec.mentor_id and rec.mentor_id.id == rec.id:
                raise ValidationError(
                    "A doctor cannot be their own mentor!"
                )

    def action_quick_visit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Book Appointment',
            'res_model': 'hr_hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
            },
        }
