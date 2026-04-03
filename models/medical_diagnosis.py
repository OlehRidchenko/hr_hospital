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
    ])

    @api.onchange("is_approved")
    def _onchange_is_approved(self):
        if self.is_approved:
            self.approved_doctor_id = self.env.user
            self.approval_date = fields.Datetime.now()
        else:
            self.approved_doctor_id = False
            self.approval_date = False
