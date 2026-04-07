from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MassReassignDoctorWizard(models.TransientModel):
    _name = "mass.reassign.doctor.wizard"
    _description = "Mass Reassign Doctor Wizard"

    old_doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Old Doctor",
    )
    new_doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="New Doctor",
        required=True,
    )
    patient_ids = fields.Many2many(
        "hr_hospital.patient",
        string="Patients",
        domain="[('personal_doctor_id', '=', old_doctor_id)]",
    )
    changed_date = fields.Date(
        required=True,
        default=fields.Date.today,
    )
    reason = fields.Text(
        string="Reason for Change",
        required=True,
    )

    @api.onchange("old_doctor_id")
    def _onchange_old_doctor(self):
        if self.old_doctor_id:
            patients = self.env["hr_hospital.patient"].search([
                ("personal_doctor_id", "=", self.old_doctor_id.id),
            ])
            self.patient_ids = patients
        else:
            self.patient_ids = False

    @api.constrains("old_doctor_id", "new_doctor_id")
    def _check_doctors_different(self):
        for rec in self:
            if (
                rec.old_doctor_id
                and rec.new_doctor_id
                and rec.old_doctor_id == rec.new_doctor_id
            ):
                raise ValidationError(
                    "Old doctor and new doctor must be different!"
                )

    def action_reassign(self):
        self.ensure_one()
        if not self.patient_ids:
            raise ValidationError(
                "Please select at least one patient to reassign!"
            )
        for patient in self.patient_ids:
            patient.write({
                "personal_doctor_id": self.new_doctor_id.id,
            })
            last_history = self.env["patient.doctor.history"].search([
                ("patient_id", "=", patient.id),
                ("doctor_id", "=", self.new_doctor_id.id),
                ("active", "=", True),
            ], limit=1)
            if last_history:
                last_history.write({
                    "reason": self.reason,
                    "assigned_date": self.changed_date,
                })
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success!",
                "message": (
                    f"{len(self.patient_ids)} patient(s) successfully "
                    f"reassigned to {self.new_doctor_id.name}."
                ),
                "sticky": False,
                "type": "success",
            },
        }
