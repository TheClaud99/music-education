# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class EducationCourse(models.Model):
    _inherit = "education.course"

    timetable_ids = fields.One2many(
        "education.timetable.line", "course_id", "Timetables", tracking=True
    )
