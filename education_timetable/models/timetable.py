# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
#                Luis Adan Jimenez Hernandez <luis.jimenez@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class EducationTimetableLine(models.Model):
    _name = "education.timetable.line"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=False, default=lambda self: _("New"))

    course_id = fields.Many2one(
        comodel_name="education.course", string="Course", required=True
    )

    group_id = fields.Many2one(comodel_name="education.group", string="Group")

    subject_id = fields.Many2one(comodel_name="education.subject", string="Subject")

    teacher_id = fields.Many2one(
        comodel_name="res.partner", string="Teacher", required=True
    )

    students = fields.Many2many(
        "res.partner",
        "students_timetable_rel",
        "timetable_id",
        "student_id",
        "Students",
    )

    timerange_id = fields.Many2one(
        comodel_name="education.timerange", string="Time Range"
    )

    start_time = fields.Float(string="Start time")
    end_time = fields.Float(string="End time")

    day_ids = fields.Many2many(
        comodel_name="education.day",
        relation="timetable_day_rel",
        column1="timetable_id",
        column2="day_id",
        string="Days",
    )

    date_from = fields.Date(
        string="Start Date", required=True, default=fields.Date.context_today
    )

    date_to = fields.Date(string="End Date", required=True)

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        string="Status",
        default="draft",
        required=True,
    )

    session_ids = fields.One2many(
        comodel_name="education.session", inverse_name="timetable_id", string="Sessions"
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        index=True,
        track_visibility="onchange",
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )

    @api.onchange("group_id")
    def _change_group_id(self):
        if not self.group_id:
            return {"domain": {"subject_id": expression.FALSE_DOMAIN}}
        subject_fields_domain = [
            ("id", "in", self.course_id.subject_ids.mapped("subject_id").ids)
        ]
        return {"domain": {"subject_id": subject_fields_domain}}

    def get_days(self, start, end):
        step = timedelta(days=1)
        for i in range((end - start).days + 1):
            yield start + i * step

    def get_hours(self, hours):
        return "{0:02.0f}:{1:02.0f}:00".format(*divmod(float(hours) * 60, 60))

    def _prepare_session_vals(self, day):
        students = self.students
        start = day.strftime("%Y-%m-%d") + " " + self.get_hours(self.start_time)
        stop = day.strftime("%Y-%m-%d") + " " + self.get_hours(self.end_time)
        duration = self.end_time - self.start_time
        tz_name = self._context.get("tz") or self.env.user.tz
        tz = pytz.timezone(tz_name)
        start = (
            tz.normalize(tz.localize(fields.Datetime.from_string(start)))
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )

        stop = (
            tz.normalize(tz.localize(fields.Datetime.from_string(stop)))
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )

        return {
            "start": start,
            "stop": stop,
            "teacher_id": self.teacher_id.id,
            "attendance_ids": [
                (0, 0, {"student_id": student.id}) for student in students
            ],
            "duration": duration,
            "timetable_id": self.id,
        }

    def generate_new_sessions(self):
        self.ensure_one()
        self.state = "done"
        session_obj = self.env["education.session"]
        event_obj = self.env["calendar.event"]
        start = fields.Date.from_string(self.date_from)
        end = fields.Date.from_string(self.date_to)

        if end < start:
            raise UserError(
                _("La data di fine non può essere minore della data di inizio")
            )

        if not self.students:
            raise UserError(_("Devi selezionare almeno uno studente"))

        days = []
        day_ids_codes = []
        for code in self.day_ids:
            day_ids_codes.append(code.code)
        for day in self.get_days(start, end):
            if day.weekday() in day_ids_codes:
                days.append(day)

        if not days:
            raise UserError(_("Nessuna lezione generabile per i giorni selezionati"))

        for day in days:
            session_obj.create(self._prepare_session_vals(day))

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("education.timetable.line")
                or "New"
            )
        return super(EducationTimetableLine, self).create(vals)

    def unlink(self):
        for record in self:
            if record.mapped("session_ids").filtered(lambda s: s.state in ["done"]):
                raise ValidationError(
                    _("You can not remove timetable with done sessions")
                )
        return super(EducationTimetableLine, self).unlink()

    @api.onchange("group_id")
    def _onchange_group_id(self):
        for record in self:
            record.date_from = record.group_id.date_from
            record.date_to = record.group_id.date_to
