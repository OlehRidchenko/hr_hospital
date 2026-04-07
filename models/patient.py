from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _name = "hr_hospital.patient"
    _description = "Patient"
    _inherit = ["abstract.person"]

    personal_doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Personal Doctor",
    )

    passport_data = fields.Char(
        size=10,
    )

    contact_person_id = fields.Many2one(
        "contact.person",
        string="Contact Person",
    )

    blood_group = fields.Selection([
        ("o_pos", "O(I) Rh+"),
        ("o_neg", "O(I) Rh-"),
        ("a_pos", "A(II) Rh+"),
        ("a_neg", "A(II) Rh-"),
        ("b_pos", "B(III) Rh+"),
        ("b_neg", "B(III) Rh-"),
        ("ab_pos", "AB(IV) Rh+"),
        ("ab_neg", "AB(IV) Rh-"),
    ])

    allergies = fields.Text()

    insurance_company_id = fields.Many2one(
        "res.partner",
        string="Insurance Company",
        domain=[("is_company", "=", True)],
    )

    insurance_policy_number = fields.Char()

    doctor_history_ids = fields.One2many(
        "patient.doctor.history",
        "patient_id",
        string="Doctor History",
    )

    quick_visit_ids = fields.One2many(
        "hr_hospital.visit",
        "patient_id",
        string="Visits",
    )

    diagnosis_history_ids = fields.One2many(
        "medical.diagnosis",
        "patient_id",
        string="Diagnosis History",
    )

    @api.constrains("birth_date")
    def _check_age(self):
        for rec in self:
            if rec.birth_date and rec.age <= 0:
                raise ValidationError(
                    "Patient age must be greater than 0!"
                )

    @api.onchange("personal_doctor_id")
    def _onchange_allergies_warning(self):
        if self.allergies and self.allergies.lower() != "none":
            return {
                "warning": {
                    "title": "Allergy Warning!",
                    "message": (
                        f"Patient {self.name or ''} has allergies:\n"
                        f"{self.allergies}"
                    ),
                }
            }

    @api.onchange("country_id")
    def _onchange_country_suggest_lang(self):
        if self.country_id:
            lang = self.env["res.lang"].search(
                [("code", "like", self.country_id.code)],
                limit=1,
            )
            if lang:
                self.lang_id = lang

    def write(self, vals):
        if "personal_doctor_id" in vals:
            for rec in self:
                old_doctor_id = rec.personal_doctor_id.id
                new_doctor_id = vals.get("personal_doctor_id")

                if old_doctor_id:
                    old_history = self.env["patient.doctor.history"].search([
                        ("patient_id", "=", rec.id),
                        ("active", "=", True),
                    ])
                    old_history.write({
                        "active": False,
                        "changed_date": fields.Date.today(),
                    })

                if new_doctor_id:
                    self.env["patient.doctor.history"].create({
                        "patient_id": rec.id,
                        "doctor_id": new_doctor_id,
                        "assigned_date": fields.Date.today(),
                        "active": True,
                    })

        return super().write(vals)

    def action_view_visits(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visit History',
            'res_model': 'hr_hospital.visit',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
