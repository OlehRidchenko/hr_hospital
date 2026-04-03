from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PatientDoctorHistory(models.Model):
    _name = "patient.doctor.history"
    _description = "Patient Doctor History"

    patient_id = fields.Many2one(
        "hr_hospital.patient",
        string="Patient",
        required=True,
        ondelete="cascade",
    )
    doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Doctor",
        required=True,
        ondelete="restrict",
    )
    assigned_date = fields.Date(
        string="Date Assigned",
        required=True,
        default=fields.Date.today,
    )
    changed_date = fields.Date(string="Date Changed")
    reason = fields.Text(string="Reason for Change")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "unique_active_patient_doctor",
            "UNIQUE(patient_id, doctor_id, active)",
            "This doctor is already actively assigned to this patient!",
        ),
    ]

    @api.constrains("assigned_date", "changed_date")
    def _check_dates(self):
        for rec in self:
            if (
                rec.changed_date
                and rec.assigned_date
                and rec.changed_date < rec.assigned_date
            ):
                raise ValidationError(
                    f"Date Changed ({rec.changed_date}) cannot be earlier "
                    f"than Date Assigned ({rec.assigned_date})!"
                )

    @api.constrains("assigned_date")
    def _check_assigned_date_not_future(self):
        for rec in self:
            if rec.assigned_date and rec.assigned_date > fields.Date.today():
                raise ValidationError(
                    "Date Assigned cannot be in the future!"
                )

    @api.model
    def create(self, vals):
        patient_id = vals.get("patient_id")
        if patient_id:
            previous = self.search([
                ("patient_id", "=", patient_id),
                ("active", "=", True),
            ])
            if previous:
                previous.write({
                    "active": False,
                    "changed_date": fields.Date.today(),
                })
        return super().create(vals)

    def write(self, vals):
        if "active" in vals and not vals["active"]:
            for _ in self:
                if not vals.get("changed_date"):
                    vals["changed_date"] = fields.Date.today()
        return super().write(vals)

    def name_get(self):
        result = []
        for rec in self:
            status = "Active" if rec.active else "Inactive"
            name = (
                f"{rec.patient_id.name} → "
                f"{rec.doctor_id.name} "
                f"({rec.assigned_date}) [{status}]"
            )
            result.append((rec.id, name))
        return result
