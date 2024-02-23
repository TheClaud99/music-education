from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # One2one field, actually
    session_ids = fields.One2many(
        comodel_name="education.session",
        inverse_name="meeting_id",
        string="Lezioni",
    )
    attendance_ids = fields.One2many(
        related="session_ids.attendance_ids", string="Presenze"
    )

    teacher_id = fields.Many2one(related="session_ids.teacher_id")
    teacher_color = fields.Integer(related="teacher_id.color")

    payment_state = fields.Selection(
        [("not_paid", "Not Paid"), ("paid", "Paid"), ("partial", "Partially Paid")],
        "Payment Status",
        compute="_compute_payment_state",
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
    )

    @api.depends("session_ids.attendance_ids.is_paid")
    def _compute_payment_state(self):
        for event in self:
            payment_exists = False
            paid = True
            for attendance in event.session_ids.attendance_ids:
                if attendance.is_paid:
                    payment_exists = True
                else:
                    paid = False

            if paid:
                event.payment_state = "paid"
                continue

            if payment_exists:
                event.payment_state = "partial"
                continue

            event.payment_state = "not_paid"

    @api.constrains("resource_booking_ids", "start", "stop")
    def _check_bookings_scheduling(self):
        """Scheduled bookings must have no conflicts."""
        sessions = self.sudo().session_ids
        return sessions._check_scheduling()

    @api.model_create_multi
    def create(self, vals_list):
        """Transfer resource booking to _attendees_values by context.

        We need to serialize the creation in that case.
        mail_notify_author key from context is necessary to force the notification
        to be sent to author.
        """
        vals_list2 = []
        records = self.env["calendar.event"]
        for vals in vals_list:
            if "session_ids" in vals:
                records += super(
                    CalendarEvent,
                    self.with_context(
                        session_ids=vals["session_ids"],
                        mail_notify_author=True,
                    ),
                ).create(vals)
            else:
                vals_list2.append(vals)
        records += super().create(vals_list2)
        return records

    def _attendees_values(self, partner_commands):
        """Autoconfirm resource attendees."""
        attendee_commands = super()._attendees_values(partner_commands)
        for command in attendee_commands:
            if command[0] != 0:
                continue
            command[2]["state"] = "accepted"
        return attendee_commands
