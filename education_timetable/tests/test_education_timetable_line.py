# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestEducationTimetableLine(TransactionCase):
    def setUp(self):
        super(TestEducationTimetableLine, self).setUp()

        # Timetable Line data
        education_timetable_obj = self.env["education.timetable.line"]
        course_id = self.env.ref("education.education_course_1")
        group_id = self.env.ref("education.education_group_1")
        teacher_id = self.env.ref("education.education_teacher_1")
        days = ("0", "Monday")
        date_from = fields.Date.today()
        date_from_datetime = fields.Date.from_string(date_from)
        date_to_datetime = date_from_datetime + datetime.timedelta(days=30)
        date_to = fields.Date.to_string(date_to_datetime)
        # Create Timetable Line
        self.education_timetable_id = education_timetable_obj.create(
            {
                "course_id": course_id.id,
                "group_id": group_id.id,
                "teacher_id": teacher_id.id,
                "days": days,
                "date_from": date_from,
                "date_to": date_to,
            }
        )

        # Generate New Sessions

    def test_generate_new_sessions(self):
        self.education_timetable_id.generate_new_sessions()
