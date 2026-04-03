import json
import csv
import io
import base64
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PatientCardExportWizard(models.TransientModel):
    _name = "patient.card.export.wizard"
    _description = "Patient Card Export Wizard"

    patient_id = fields.Many2one(
        "hr_hospital.patient",
        string="Patient",
        required=True,
    )
    date_from = fields.Date()
    date_to = fields.Date()

    include_diagnoses = fields.Boolean(
        default=True,
    )
    include_recommendations = fields.Boolean(
        default=True,
    )
    lang_id = fields.Many2one(
        "res.lang",
        string="Report Language",
    )
    export_format = fields.Selection([
        ("json", "JSON"),
        ("csv", "CSV"),
    ], default="json", required=True)

    export_file = fields.Binary(readonly=True)
    export_filename = fields.Char(string="Filename", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        patient_id = self.env.context.get("active_id")
        if patient_id:
            patient = self.env["hr_hospital.patient"].browse(patient_id)
            res["patient_id"] = patient_id
            if patient.lang_id:
                res["lang_id"] = patient.lang_id.id
        return res

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError(
                        "Date From cannot be later than Date To!"
                    )

    # ===== METHODS =====
    def _get_patient_data(self):
        self.ensure_one()
        patient = self.patient_id

        data = {
            "patient": {
                "name": patient.name,
                "birth_date": str(patient.birth_date or ""),
                "age": patient.age,
                "gender": patient.gender or "",
                "blood_group": patient.blood_group or "",
                "allergies": patient.allergies or "",
                "passport_data": patient.passport_data or "",
                "phone": patient.phone or "",
                "email": patient.email or "",
                "personal_doctor": patient.personal_doctor_id.name or "",
                "insurance_company": (
                    patient.insurance_company_id.name or ""
                ),
                "insurance_policy": patient.insurance_policy_number or "",
            },
            "visits": [],
        }

        visit_domain = [("patient_id", "=", patient.id)]
        if self.date_from:
            visit_domain.append(
                ("planned_datetime", ">=", self.date_from)
            )
        if self.date_to:
            visit_domain.append(
                ("planned_datetime", "<=", self.date_to)
            )

        visits = self.env["hr_hospital.visit"].search(visit_domain)

        for visit in visits:
            visit_data = {
                "date": str(visit.planned_datetime or ""),
                "doctor": visit.doctor_id.name or "",
                "status": visit.status or "",
                "visit_type": visit.visit_type or "",
                "cost": visit.cost,
            }

            if self.include_diagnoses:
                visit_data["diagnoses"] = [
                    {
                        "disease": d.disease_id.name or "",
                        "severity": d.severity or "",
                        "description": d.description or "",
                        "is_approved": d.is_approved,
                        "approved_by": d.approved_doctor_id.name or "",
                    }
                    for d in visit.diagnosis_ids
                ]

            if self.include_recommendations:
                visit_data["recommendations"] = visit.recommendations or ""

            data["visits"].append(visit_data)

        return data

    def action_export(self):
        self.ensure_one()
        patient_data = self._get_patient_data()
        patient_name = self.patient_id.name.replace(" ", "_")

        if self.export_format == "json":
            content = json.dumps(patient_data, ensure_ascii=False, indent=2)
            filename = f"patient_card_{patient_name}.json"
            file_content = base64.b64encode(content.encode("utf-8"))

        else:
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(["=== PATIENT INFO ==="])
            for key, val in patient_data["patient"].items():
                writer.writerow([key, val])

            writer.writerow([])
            writer.writerow(["=== VISITS ==="])
            writer.writerow([
                "Date", "Doctor", "Status",
                "Type", "Cost", "Disease",
                "Severity", "Approved",
            ])
            for visit in patient_data["visits"]:
                diagnoses = visit.get("diagnoses", [{}])
                for diag in diagnoses or [{}]:
                    writer.writerow([
                        visit.get("date", ""),
                        visit.get("doctor", ""),
                        visit.get("status", ""),
                        visit.get("visit_type", ""),
                        visit.get("cost", ""),
                        diag.get("disease", ""),
                        diag.get("severity", ""),
                        diag.get("is_approved", ""),
                    ])

            filename = f"patient_card_{patient_name}.csv"
            file_content = base64.b64encode(
                output.getvalue().encode("utf-8")
            )

        self.write({
            "export_file": file_content,
            "export_filename": filename,
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
