from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Disease(models.Model):
    _name = "hr_hospital.disease"
    _description = "Disease"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(string="Disease Name", required=True)
    description = fields.Text()

    parent_id = fields.Many2one(
        "hr_hospital.disease",
        string="Parent Disease",
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        "hr_hospital.disease",
        "parent_id",
        string="Sub-diseases",
    )
    parent_path = fields.Char(index=True, unaccent=False)

    icd10_code = fields.Char(string="ICD-10 Code", size=10)

    danger_level = fields.Selection([
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ])

    is_contagious = fields.Boolean(string="Contagious")
    symptoms = fields.Text()

    country_ids = fields.Many2many(
        "res.country",
        string="Regions of Spread",
    )

    _sql_constraints = [
        (
            "icd10_code_unique",
            "UNIQUE(icd10_code)",
            "ICD-10 code must be unique!",
        ),
    ]

    @api.constrains("parent_id")
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                "Error! You cannot create a recursive disease hierarchy."
            )

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.parent_id:
                name = f"{rec.parent_id.name} / {name}"
            if rec.icd10_code:
                name = f"[{rec.icd10_code}] {name}"
            result.append((rec.id, name))
        return result
