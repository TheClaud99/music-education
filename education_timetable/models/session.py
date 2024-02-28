import calendar
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class EducationSession(models.Model):
    _name = "education.session"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Resource Booking"
    _order = "start DESC"
    _sql_constraints = [
        (
            "unique_meeting_id",
            "UNIQUE(meeting_id)",
            "Only one event per resource booking can exist.",
        ),
    ]

    _rec_name = "code"

    code = fields.Char(string="Code")
    timetable_id = fields.Many2one(
        comodel_name="education.timetable.line",
        string="Timetable Lines",
        ondelete="cascade",
        index=True,
        copy=False,
        required=True,
    )
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
        string="Insegnante",
        index=True,
        ondelete="cascade",
        required=True,
        tracking=True,
        help="Who requested this booking?",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    active = fields.Boolean(default=True)
    meeting_id = fields.Many2one(
        comodel_name="calendar.event",
        string="Meeting",
        context={"default_res_id": False, "default_res_model": False},
        copy=False,
        index=True,
        ondelete="cascade",
        help="Meeting confirmed for this booking.",
    )
    categ_ids = fields.Many2many(string="Tags", comodel_name="calendar.event.type")
    name = fields.Char(index=True, help="Leave empty to autogenerate a booking name.")
    description = fields.Html()
    user_id = fields.Many2one(
        comodel_name="res.users",
        default=lambda self: self._default_user_id(),
        store=True,
        readonly=False,
        compute="_compute_user_id",
        string="Organizer",
        index=True,
        tracking=True,
        help=(
            "Who organized this booking? Usually whoever created the record. "
            "It will appear as the calendar event organizer, when scheduled, "
            "and calendar notifications will be sent in his/her name."
        ),
    )

    start = fields.Datetime(
        compute="_compute_start",
        copy=False,
        index=True,
        readonly=False,
        store=True,
        tracking=True,
    )
    duration = fields.Float(
        compute="_compute_duration",
        readonly=False,
        store=True,
        tracking=True,
        help="Amount of time that the resources will be booked and unavailable for others.",
    )
    stop = fields.Datetime(
        compute="_compute_stop",
        copy=False,
        index=True,
        store=True,
        tracking=True,
    )

    @api.model
    def _default_user_id(self):
        return self.env.user

    @api.depends("name", "teacher_id", "meeting_id")
    @api.depends_context("uid", "using_portal")
    def _compute_display_name(self):
        """Overridden just for dependencies; see `name_get()` for implementation."""
        return super()._compute_display_name()

    @api.depends("meeting_id.start")
    def _compute_start(self):
        """Get start date from related meeting, if available."""
        for record in self:
            if record.id:
                record.start = record.meeting_id.start

    @api.depends("meeting_id.duration")
    def _compute_duration(self):
        """Compute duration for each booking."""
        for record in self:
            # Special case when creating record from UI
            if not record.id:
                if record.timetable_id:
                    duration = (
                        record.timetable_id.end_time - record.timetable_id.start_time
                    )
                else:
                    duration = 0.0
                record.duration = self.default_get(["duration"]).get(
                    "duration", duration
                )
            # Get duration from type only when changing type or when creating from ORM
            elif (
                not record.duration
                or record._origin.timetable_id != record.timetable_id
            ):
                duration = record.timetable_id.end_time - record.timetable_id.start_time
                record.duration = duration
            # Get it from meeting only when available
            elif record.meeting_id:
                record.duration = record.meeting_id.duration

    @api.depends("start", "duration")
    def _compute_stop(self):
        """Get stop date from start date and duration."""
        for record in self:
            try:
                record.stop = record.start + timedelta(hours=record.duration)
            except TypeError:
                # Either value is False: no stop date
                record.stop = False

    @api.depends("meeting_id.user_id")
    def _compute_user_id(self):
        """Get user from related meeting, if available."""
        for record in self.filtered(lambda x: x.meeting_id.user_id):
            record.user_id = record.meeting_id.user_id

    def _prepare_meeting_vals(self):
        students = self.attendance_ids.mapped("student_id")

        return dict(
            # alarm_ids=[(6, 0, self.type_id.alarm_ids.ids)],
            # categ_ids=[(6, 0, self.categ_ids.ids)],
            # description=self.type_id.requester_advice,
            duration=self.duration,
            # location=self.location,
            name=self.name or self._get_name_formatted(self.teacher_id, students),
            partner_ids=[(4, partner.id, 0) for partner in self.teacher_id | students],
            session_ids=[(6, 0, self.ids)],
            start=self.start,
            stop=self.stop,
            user_id=self.env.user.id,
            show_as="busy",
            # These 2 avoid creating event as activity
            res_model_id=False,
            res_id=False,
        )

    def _sync_meeting(self):
        """Lazy-create or destroy calendar.event."""
        # Notify changed dates to attendees
        _self = self.with_context(syncing_booking_ids=self.ids)
        # Avoid sync recursion
        _self -= self.browse(self.env.context.get("syncing_booking_ids"))
        to_create, to_delete = [], _self.env["calendar.event"]
        for one in _self:
            if one.start:
                meeting_vals = one._prepare_meeting_vals()
                if one.meeting_id:
                    meeting = one.meeting_id
                    if not all(
                        (
                            one.meeting_id.start == one.start,
                            one.meeting_id.stop == one.stop,
                            one.meeting_id.duration == one.duration,
                        )
                    ):
                        # Context to notify scheduling change
                        meeting = meeting.with_context(from_ui=True)
                    meeting.write(meeting_vals)
                else:
                    to_create.append(meeting_vals)
            else:
                to_delete |= one.meeting_id
        to_delete.unlink()
        _self.env["calendar.event"].create(to_create)

    @api.constrains("combination_id", "meeting_id")
    def _check_scheduling(self):
        """Scheduled bookings must have no conflicts."""
        # Nothing to do if no bookings are scheduled
        # todo: to implement
        pass

    def _get_calendar_context(self, year=None, month=None, now=None):
        """Get the required context for the calendar view in the portal.

        See the `resource_booking.scheduling_calendar` view.

        :param int year: Year of the calendar to be displayed.
        :param int month: Month of the calendar to be displayed.
        :param datetime now: Represents the current datetime.
        """
        month1 = relativedelta(months=1)
        now = now or fields.Datetime.now()
        year = year or now.year
        month = month or now.month
        start = datetime(year, month, 1)
        start, now = (
            fields.Datetime.context_timestamp(self, dt) for dt in (start, now)
        )
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        lang = self.env["res.lang"]._lang_get(self.env.lang or self.env.user.lang)
        weekday_names = dict(lang.fields_get(["week_start"])["week_start"]["selection"])
        slots = self._get_available_slots(start, start + month1)
        return {
            "booking": self,
            "calendar": calendar.Calendar(int(lang.week_start) - 1),
            "now": now,
            "res_lang": lang,
            "slots": slots,
            "start": start,
            "weekday_names": weekday_names,
        }

    @api.model
    def _get_name_formatted(self, teacher, students, meeting=None):
        """Produce a beautifully formatted name."""
        values = {
            "teacher": teacher.display_name,
            "students": ", ".join(students.mapped("display_name")),
        }
        if meeting:
            values["time"] = meeting.display_time
            return _("%(students)s - %(teacher)s - %(time)s") % values
        return _("%(students)s - %(teacher)s") % values

    @api.model_create_multi
    def create(self, vals_list):
        """Sync booking with meeting if needed."""
        result = super().create(vals_list)
        result._sync_meeting()
        return result

    def write(self, vals):
        """Sync booking with meeting if needed."""
        result = super().write(vals)
        self._sync_meeting()
        return result

    def unlink(self):
        """Unlink meeting if needed."""
        meeting = self.meeting_id
        ret = super().unlink()
        # elimino il meeting dopo la session perché
        # altrimenti avverrebbe l'ondelete cascade su meeting_id
        meeting.unlink()
        return ret

    def name_get(self):
        """Autogenerate booking name if none is provided."""
        old = super().name_get()
        new = []
        for id_, name in old:
            record = self.browse(id_)
            if self.env.context.get("using_portal"):
                # ID optionally suffixed with custom name for portal users
                template = _("# %(id)d - %(name)s") if record.name else _("# %(id)d")
                name = template % {"id": id_, "name": name}
            elif not record.name:
                # Automatic name for backend users
                students = record.attendance_ids.mapped("student_id")
                name = self._get_name_formatted(
                    record.teacher_id, students, record.meeting_id
                )
            new.append((id_, name))
        return new

    def _message_get_suggested_recipients(self):
        """Suggest related partners."""
        recipients = super()._message_get_suggested_recipients()
        for record in self:
            record._message_add_suggested_recipient(
                recipients,
                partner=record.teacher_id,
                reason=self._fields["teacher_id"].string,
            )
        return recipients

    def action_schedule(self):
        """Redirect user to a simpler way to schedule this booking."""
        FloatTimeParser = self.env["ir.qweb.field.float_time"]
        return {
            "context": dict(
                self.env.context,
                # These 2 avoid creating event as activity
                default_res_model_id=False,
                default_res_id=False,
                # Context used by web_calendar_slot_duration module
                calendar_slot_duration=FloatTimeParser.value_to_html(
                    self.duration, False
                ),
                default_resource_booking_ids=[(6, 0, self.ids)],
                default_name=self.name,
            ),
            "name": _("Schedule booking"),
            "res_model": "calendar.event",
            "target": "self",
            "type": "ir.actions.act_window",
            "view_mode": "calendar,tree,form",
        }

    def action_confirm(self):
        """Confirm own and requesting partner's attendance."""
        attendees_to_confirm = self.env["calendar.attendee"]
        confirm_always = self.env["res.partner"]
        if self.env.context.get("confirm_own_attendance"):
            confirm_always |= self.env.user.partner_id
        # Avoid wasted state recomputes
        with self.env.norecompute():
            for booking in self:
                if not booking.meeting_id:
                    continue
                # Make sure requester and user resources are meeting attendees
                booking.meeting_id.partner_ids |= booking.teacher_id | booking.mapped(
                    "attendance_ids.student_id"
                )
                # Find meeting attendees that should be confirmed
                partners_to_confirm = confirm_always | booking.teacher_id
                for attendee in booking.meeting_id.attendee_ids:
                    if attendee.partner_id & partners_to_confirm:
                        # attendee.state='accepted'
                        attendees_to_confirm |= attendee
            attendees_to_confirm.write({"state": "accepted"})
        self.flush_recordset()

    def action_unschedule(self):
        """Remove associated meetings."""
        self.mapped("meeting_id").unlink()
        # Force recomputing, in case meeting_id is not visible in the form
        self.write({"meeting_id": False})

    def action_cancel(self):
        """Cancel this booking."""
        # Remove related meeting
        self.action_unschedule()
        # Archive and reset access token
        self.write({"active": False, "access_token": False})

    def action_open_portal(self):
        return {
            "target": "self",
            "type": "ir.actions.act_url",
            "url": self.get_portal_url(),
        }
