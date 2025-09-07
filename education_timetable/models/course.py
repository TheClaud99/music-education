from odoo import fields, models


class EducationCourse(models.Model):
    _inherit = "education.course"

    timetable_ids = fields.One2many(
        "education.timetable.line", "course_id", "Timetables", tracking=True
    )
