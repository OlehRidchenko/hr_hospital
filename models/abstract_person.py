from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class AbstractPerson(models.AbstractModel):
    _name = "abstract.person"
    _description = "Abstract Person"
    _inherit = ["image.mixin"]

    last_name = fields.Char(required=True)
    first_name = fields.Char(required=True)
    middle_name = fields.Char()

    name = fields.Char(
        string="Full Name",
        compute="_compute_name",
        store=True,
    )

    phone = fields.Char()
    email = fields.Char()

    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ])

    birth_date = fields.Date()

    age = fields.Integer(compute="_compute_age")

    country_id = fields.Many2one(
        "res.country",
        string="Country of Citizenship",
    )

    lang_id = fields.Many2one(
        "res.lang",
        string="Communication Language",
    )

    @api.depends("last_name", "first_name", "middle_name")
    def _compute_name(self):
        for rec in self:
            parts = filter(None, [
                rec.last_name,
                rec.first_name,
                rec.middle_name,
            ])
            rec.name = " ".join(parts)

    @api.depends("birth_date")
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.birth_date:
                rec.age = relativedelta(today, rec.birth_date).years
            else:
                rec.age = 0
