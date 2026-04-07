from odoo import models, fields


class ContactPerson(models.Model):
    _name = "contact.person"
    _description = "Contact Person"
    _inherit = ["abstract.person"]

    relationship = fields.Selection([
        ("spouse", "Spouse"),
        ("parent", "Parent"),
        ("child", "Child"),
        ("sibling", "Sibling"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ])

    notes = fields.Text()
