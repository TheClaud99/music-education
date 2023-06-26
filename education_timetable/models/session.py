# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
#                Luis Adan Jimenez Hernandez <luis.jimenez@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta

import pytz
from odoo import api, fields, models

tz = pytz.timezone("Europe/Madrid")


class EducationSession(models.Model):
    _name = "education.session"
    _inherit = ["mail.thread"]
    _rec_name = "code"

    code = fields.Char(string="Code")
    timetable_id = fields.Many2one(
        comodel_name="education.timetable.line",
        string="Timetable Lines",
        ondelete="cascade",
    )
    date = fields.Date(string="Date")
    start_time = fields.Datetime(string="Start time", compute="_compute_time")
    end_time = fields.Datetime(string="End time", compute="_compute_time")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")], string="Status", default="draft"
    )
    attendance_ids = fields.One2many(
        comodel_name="education.session.attendance",
        inverse_name="session_id",
        string="Presenze",
    )

    teacher_id = fields.Many2one(
        comodel_name="res.partner",
        # related='timetable_id.teacher_id',
        string="Teacher",
    )
    subject_id = fields.Many2one(
        comodel_name="education.subject",
        related="timetable_id.subject_id",
        string="Subject",
    )
    group_id = fields.Many2one(
        comodel_name="education.group", related="timetable_id.group_id", string="Group"
    )
    timerange_id = fields.Many2one(
        comodel_name="education.timerange", string="Timerange"
    )
    teacher_assist = fields.Boolean(string="Teacher Assist")

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )

    
    def get_hours(self, hours):
        return "{0:02.0f}:{1:02.0f}:00".format(*divmod(float(hours) * 60, 60))

    @api.model
    def create(self, vals):
        if vals.get("code", "New") == "New":
            vals["code"] = (
                self.env["ir.sequence"].next_by_code("education.session") or "New"
            )
        return super(EducationSession, self).create(vals)

    @api.depends(
        "date",
        "timetable_id.timerange_id.start_time",
        "timetable_id.timerange_id.end_time",
    )
    def _compute_time(self):
        utc = pytz.timezone("UTC")
        for session in self.filtered(lambda s: s.timetable_id and s.date):
            start_time = session.timetable_id.timerange_id.start_time
            start_time = session.get_hours(start_time)
            end_time = session.timetable_id.timerange_id.end_time
            end_time = session.get_hours(end_time)
            date_start = session.date + " " + start_time
            date_end = session.date + " " + end_time
            start_date = tz.normalize(
                tz.localize(fields.Datetime.from_string(date_start))
            ).astimezone(utc)
            end_date = tz.normalize(
                tz.localize(fields.Datetime.from_string(date_end))
            ).astimezone(utc)
            session.start_time = start_date
            session.end_time = end_date
