from odoo import models, fields, api


class MedicalDiagnosis(models.Model):
    _name = "medical.diagnosis"
    _description = "Medical Diagnosis"

    visit_id = fields.Many2one(
        "hr_hospital.visit",
        string="Visit",
        required=True,
        ondelete="cascade",
    )
    disease_id = fields.Many2one(
        "hr_hospital.disease",
        string="Disease",
    )

    doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Doctor",
        related="visit_id.doctor_id",
        store=True,
    )
    patient_id = fields.Many2one(
        "hr_hospital.patient",
        string="Patient",
        related="visit_id.patient_id",
        store=True,
    )

    description = fields.Text(string="Diagnosis Description")
    treatment = fields.Html(string="Prescribed Treatment")

    is_approved = fields.Boolean(
        string="Approved",
        default=False,
    )
    approved_doctor_id = fields.Many2one(
        "hr_hospital.doctor",
        string="Approved by Doctor",
        readonly=True,
    )
    approval_datetime = fields.Datetime(
        string="Approval Date",
        readonly=True,
    )
    severity = fields.Selection([
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
        ("critical", "Critical"),
    ], string="Severity")

    @api.onchange("is_approved")
    def _onchange_is_approved(self):
        if self.is_approved:
            doctor = self.env["hr_hospital.doctor"].search(
                [("user_id", "=", self.env.user.id)],
                limit=1,
            )
            self.approved_doctor_id = doctor
            self.approval_datetime = fields.Datetime.now()
        else:
            self.approved_doctor_id = False
            self.approval_datetime = False

    @api.model
    def create(self, vals):
        if vals.get("is_approved"):
            doctor = self._get_current_doctor()
            vals.update({
                "approved_doctor_id": doctor.id if doctor else False,
                "approval_datetime": fields.Datetime.now(),
            })
        else:
            vals.update({
                "approved_doctor_id": False,
                "approval_datetime": False,
            })
        return super().create(vals)

    def _get_current_doctor(self):
        return self.env["hr_hospital.doctor"].search(
            [("user_id", "=", self.env.uid)],
            limit=1,
        )
