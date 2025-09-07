from odoo import fields, models


class EducationRecord(models.Model):
    _inherit = "education.record"

    pack = fields.Boolean(string="Pack", related="course_id.pack")
    parent_record_id = fields.Many2one(
        comodel_name="education.record", string="Parent Record"
    )
    pack_record_ids = fields.One2many(
        comodel_name="education.record",
        inverse_name="parent_record_id",
        string="Pack Record",
    )
