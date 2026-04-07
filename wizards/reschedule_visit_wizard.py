from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class RescheduleVisitWizard(models.TransientModel):
    _name = "reschedule.visit.wizard"
    _description = "Reschedule Visit Wizard"

    visit_id = fields.Many2one(
        "hr_hospital.visit",
        string="Current Visit",
        readonly=True,
        required=True,
    )
    new_doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="New Doctor",
        domain=[("license_number", "!=", False)],
    )
    new_date = fields.Date(
        required=True,
    )
    new_time = fields.Float(
        required=True,
    )
    reason = fields.Text(
        string="Reason for Reschedule",
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        visit_id = self.env.context.get("active_id")
        if visit_id:
            res["visit_id"] = visit_id
        return res

    @api.constrains("visit_id")
    def _check_visit_not_completed(self):
        for rec in self:
            if rec.visit_id.status == "completed":
                raise ValidationError(
                    "Cannot reschedule a completed visit!"
                )

    @api.constrains("new_date")
    def _check_new_date_future(self):
        for rec in self:
            if rec.new_date < fields.Date.today():
                raise ValidationError(
                    "New visit date must be in the future!"
                )

    def action_reschedule(self):
        self.ensure_one()
        visit = self.visit_id

        hours = int(self.new_time)
        minutes = int((self.new_time % 1) * 60)
        new_datetime = datetime.combine(
            self.new_date,
            datetime.min.time().replace(hour=hours, minute=minutes),
        )

        visit.write({
            "status": "cancelled",
            "notes": (
                f"{visit.notes or ''}\n"
                f"Rescheduled. Reason: {self.reason}"
            ).strip(),
        })

        new_visit = self.env["hr_hospital.visit"].create({
            "patient_id": visit.patient_id.id,
            "doctor_id": (
                self.new_doctor_id.id
                if self.new_doctor_id
                else visit.doctor_id.id
            ),
            "planned_datetime": new_datetime,
            "visit_type": visit.visit_type,
            "status": "planned",
            "notes": f"Rescheduled from visit #{visit.id}. Reason:"
                     f" {self.reason}",
            "currency_id": visit.currency_id.id,
            "cost": visit.cost,
        })

        return {
            "type": "ir.actions.act_window",
            "name": "New Visit",
            "res_model": "hr_hospital.visit",
            "res_id": new_visit.id,
            "view_mode": "form",
        }
