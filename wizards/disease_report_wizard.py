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
        required=True,
    )
    date_to = fields.Date(
        required=True,
    )
    report_type = fields.Selection([
        ("detailed", "Detailed"),
        ("summary", "Summary"),
    ], default="detailed")

    group_by = fields.Selection([
        ("doctor", "By Doctor"),
        ("disease", "By Disease"),
        ("month", "By Month"),
        ("country", "By Country"),
    ], default="doctor")

    result_ids = fields.Many2many(
        "medical.diagnosis",
        string="Results",
        compute="_compute_results",
    )
    result_count = fields.Integer(
        string="Total Results",
        compute="_compute_results",
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(
                    "Date From cannot be later than Date To!"
                )

    @api.depends(
        "doctor_ids", "disease_ids", "country_ids",
        "date_from", "date_to"
    )
    def _compute_results(self):
        for rec in self:
            diagnoses = rec._get_diagnoses()
            rec.result_ids = diagnoses
            rec.result_count = len(diagnoses)

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
                (
                    "visit_id.patient_id.country_id",
                    "in",
                    self.country_ids.ids,
                )
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
            "name": "Disease Report",
            "res_model": "medical.diagnosis",
            "view_mode": "list,form",
            "domain": [("id", "in", diagnoses.ids)],
            "context": {
                "group_by": self.group_by,
                "report_type": self.report_type,
            },
        }
