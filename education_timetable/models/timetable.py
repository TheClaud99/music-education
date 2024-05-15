from datetime import timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command

LOCKED_FIELD_STATES = {state: [("readonly", True)] for state in ["done"]}


class EducationTimetableLine(models.Model):
    _name = "education.timetable.line"
    _inherit = ["mail.thread"]

    name = fields.Char(required=False, default=lambda self: _("New"))

    course_id = fields.Many2one(
        comodel_name="education.course",
        string="Course",
        required=True,
        states=LOCKED_FIELD_STATES,
    )

    teacher_id = fields.Many2one(
        comodel_name="res.partner",
        string="Teacher",
        required=True,
        states=LOCKED_FIELD_STATES,
    )

    students = fields.Many2many(
        "res.partner",
        "students_timetable_rel",
        "timetable_id",
        "student_id",
        states=LOCKED_FIELD_STATES,
    )

    start_time = fields.Float(
        string="Start time",
        states=LOCKED_FIELD_STATES,
    )
    end_time = fields.Float(
        string="End time",
        states=LOCKED_FIELD_STATES,
    )

    day_ids = fields.Many2many(
        comodel_name="education.day",
        relation="timetable_day_rel",
        column1="timetable_id",
        column2="day_id",
        string="Days",
        states=LOCKED_FIELD_STATES,
    )

    date_from = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.context_today,
        states=LOCKED_FIELD_STATES,
    )

    date_to = fields.Date(
        string="End Date",
        required=True,
        states=LOCKED_FIELD_STATES,
    )

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        string="Status",
        default="draft",
        required=True,
    )

    session_ids = fields.One2many(
        "education.session",
        "timetable_id",
        "Sessions",
        copy=True,
        states=LOCKED_FIELD_STATES,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    def get_days(self, start, end):
        step = timedelta(days=1)
        for i in range((end - start).days + 1):
            yield start + i * step

    def get_hours(self, hours):
        return "{:02.0f}:{:02.0f}:00".format(*divmod(float(hours) * 60, 60))

    def _prepare_meeting_vals(self, day):
        students = self.students
        teacher = self.teacher_id
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
            "duration": duration,
            "name": self.env["education.session"]._get_name_formatted(
                teacher, students
            ),
            "partner_ids": [Command.link(partner.id) for partner in teacher | students],
            "start": start,
            "stop": stop,
            "user_id": self.env.user.id,
            "show_as": "busy",
            "res_model_id": False,
            "res_id": False,
        }

    def _prepare_session_vals(self, meeting):
        students = self.students
        return {
            "teacher_id": self.teacher_id.id,
            "attendance_ids": [
                Command.create({"student_id": student.id}) for student in students
            ],
            "meeting_id": meeting.id,
            "timetable_id": self.id,
        }

    def action_cancel(self):
        for timetable in self:
            timetable.session_ids.unlink()
            timetable.state = "draft"

    def generate_new_sessions(self):
        self.ensure_one()
        self.state = "done"
        session_obj = self.env["education.session"]
        meeting_obj = self.env["calendar.event"].with_context(no_mail_to_attendees=True)
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
            meeting = meeting_obj.create(self._prepare_meeting_vals(day))
            session_obj.create(self._prepare_session_vals(meeting))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("education.timetable.line")
                    or "New"
                )
        return super(EducationTimetableLine, self).create(vals)

    def unlink(self):
        for record in self:
            if record.session_ids.filtered(lambda s: s.state in ["done"]):
                raise ValidationError(
                    _("You can not remove timetable with done sessions")
                )
        self.session_ids.unlink()
        return super(EducationTimetableLine, self).unlink()
