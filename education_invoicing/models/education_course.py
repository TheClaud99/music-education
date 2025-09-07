from odoo import fields, models


class EducationCourse(models.Model):
    _inherit = "education.course"

    invoicing_method_ids = fields.One2many(
        comodel_name="education.invoicing.method",
        inverse_name="course_id",
        string="Invoicing Methods",
    )
