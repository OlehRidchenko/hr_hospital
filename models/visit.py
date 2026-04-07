from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Visit(models.Model):
    _name = "hr_hospital.visit"
    _description = "Patient Visit"

    patient_id = fields.Many2one(
        "hr_hospital.patient",
        string="Patient",
        required=True,
    )
    doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Doctor",
        required=True,
        domain=[("license_number", "!=", False)],
    )
    status = fields.Selection([
        ("planned", "Planned"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ], default="planned")

    planned_datetime = fields.Datetime(
        string="Planned Date & Time",
    )
    actual_datetime = fields.Datetime(
        string="Actual Date & Time",
    )
    visit_type = fields.Selection([
        ("primary", "Primary"),
        ("repeated", "Repeated"),
        ("preventive", "Preventive"),
        ("urgent", "Urgent"),
    ])

    diagnosis_ids = fields.One2many(
        "medical.diagnosis",
        "visit_id",
        string="Diagnoses",
    )

    diagnosis_count = fields.Integer(
        compute="_compute_diagnosis_count",
        store=True,
    )

    recommendations = fields.Html()

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    cost = fields.Monetary(
        string="Visit Cost",
        currency_field="currency_id",
    )
    notes = fields.Text()

    @api.depends("diagnosis_ids")
    def _compute_diagnosis_count(self):
        for rec in self:
            rec.diagnosis_count = len(rec.diagnosis_ids)

    @api.onchange("patient_id")
    def _onchange_patient_allergy_warning(self):
        if (
            self.patient_id
            and self.patient_id.allergies
            and self.patient_id.allergies.lower() != "none"
        ):
            return {
                "warning": {
                    "title": "Allergy Warning!",
                    "message": (
                        f"Patient '{self.patient_id.name}' has allergies:\n"
                        f"{self.patient_id.allergies}"
                    ),
                }
            }

    @api.constrains("patient_id", "doctor_id", "planned_datetime")
    def _check_one_visit_per_day(self):
        for rec in self:
            if not rec.planned_datetime:
                continue
            date_start = rec.planned_datetime.replace(
                hour=0, minute=0, second=0
            )
            date_end = rec.planned_datetime.replace(
                hour=23, minute=59, second=59
            )
            duplicate = self.env["hr_hospital.visit"].search([
                ("id", "!=", rec.id),
                ("patient_id", "=", rec.patient_id.id),
                ("doctor_id", "=", rec.doctor_id.id),
                ("planned_datetime", ">=", date_start),
                ("planned_datetime", "<=", date_end),
                ("status", "not in", ["cancelled"]),
            ])
            if duplicate:
                raise ValidationError(
                    f"Patient '{rec.patient_id.name}' already has a visit "
                    f"with doctor '{rec.doctor_id.name}' on "
                    f"{rec.planned_datetime.date()}!"
                )

    @api.constrains("status", "doctor_id",
                    "planned_datetime", "actual_datetime")
    def _check_completed_visit_immutable(self):
        for rec in self:
            if rec.status == "completed":
                original = rec._origin
                if not original:
                    continue
                if (
                    original.doctor_id
                    and original.doctor_id != rec.doctor_id
                ):
                    raise ValidationError(
                        "Cannot change the doctor of a completed visit!"
                    )
                if (
                    original.planned_datetime
                    and original.planned_datetime != rec.planned_datetime
                ):
                    raise ValidationError(
                        "Cannot change the date/time of a completed visit!"
                    )

    def unlink(self):
        for rec in self:
            if rec.diagnosis_ids:
                raise ValidationError(
                    f"Cannot delete visit of '{rec.patient_id.name}' "
                    f"because it has {len(rec.diagnosis_ids)} diagnosis(es)!\n"
                    f"Please remove diagnoses first."
                )
        return super().unlink()

    def action_complete(self):
        for rec in self:
            if rec.status == "completed":
                raise ValidationError(
                    "Visit is already completed!"
                )
            rec.status = "completed"
            rec.actual_datetime = fields.Datetime.now()

    def action_cancel(self):
        for rec in self:
            if rec.status == "completed":
                raise ValidationError(
                    "Cannot cancel a completed visit!"
                )
            rec.status = "cancelled"

    def action_no_show(self):
        for rec in self:
            if rec.status == "completed":
                raise ValidationError(
                    "Cannot mark a completed visit as no show!"
                )
            rec.status = "no_show"

    def _get_available_doctors(self, speciality_id=None):
        domain = [("license_number", "!=", False)]
        if speciality_id:
            domain.append(("speciality_id", "=", speciality_id))
        return self.env["hr_hospital.doctor"].search(domain)

    def _get_available_dates(self, doctor_id):
        if not doctor_id:
            return []
        unavailable = self.env["doctor.schedule"].search([
            ("doctor_id", "=", doctor_id),
            ("schedule_type", "in", ["vacation", "sick_leave"]),
        ]).mapped("date")
        return unavailable
