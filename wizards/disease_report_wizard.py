from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DiseaseReportWizard(models.TransientModel):
    _name = "disease.report.wizard"
    _description = "Disease Report Wizard"

    doctor_ids = fields.Many2many(
        "hr_hospital.doctor",
        string="Doctors",
    )
    disease_ids = fields.Many2many(
        "hr_hospital.disease",
        string="Diseases",
    )
    country_ids = fields.Many2many(
        "res.country",
        string="Countries",
    )
    date_from = fields.Date(
        string="Date From",
        required=True,
    )
    date_to = fields.Date(
        string="Date To",
        required=True,
    )
    report_type = fields.Selection([
        ("detailed", "Detailed"),
        ("summary", "Summary"),
    ], string="Report Type", default="detailed")

    group_by = fields.Selection([
        ("disease_id", "By Disease"),
        ("severity", "By Severity"),
        ("is_approved", "By Approval Status"),
        ("doctor_id", "By Doctor"),
    ], string="Group By", default="disease_id")

    result_count = fields.Integer(
        string="Total Results",
        compute="_compute_result_count",
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(
                    "Date From cannot be later than Date To!"
                )

    @api.depends("doctor_ids", "disease_ids", "country_ids",
                 "date_from", "date_to")
    def _compute_result_count(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                rec.result_count = len(rec._get_diagnoses())
            else:
                rec.result_count = 0

    def _get_diagnoses(self):
        self.ensure_one()
        domain = [
            ("visit_id.planned_datetime", ">=", self.date_from),
            ("visit_id.planned_datetime", "<=", self.date_to),
        ]
        if self.doctor_ids:
            domain.append(
                ("visit_id.doctor_id", "in", self.doctor_ids.ids)
            )
        if self.disease_ids:
            domain.append(
                ("disease_id", "in", self.disease_ids.ids)
            )
        if self.country_ids:
            domain.append(
                ("visit_id.patient_id.country_id", "in",
                 self.country_ids.ids)
            )
        return self.env["medical.diagnosis"].search(domain)

    def action_generate_report(self):
        self.ensure_one()
        diagnoses = self._get_diagnoses()
        if not diagnoses:
            raise ValidationError(
                "No diagnoses found for the selected criteria!"
            )
        return {
            "type": "ir.actions.act_window",
            "name": f"Disease Report ({self.date_from} – {self.date_to})",
            "res_model": "medical.diagnosis",
            "view_mode": "list,form",
            "domain": [("id", "in", diagnoses.ids)],
            "context": {"search_default_group_disease": 1},
        }
