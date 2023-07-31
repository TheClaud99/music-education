# Copyright 2021 Tecnativa - Jairo Llopis
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    # One2one field, actually
    session_ids = fields.One2many(
        comodel_name="education.session",
        inverse_name="meeting_id",
        string="Lezioni",
    )

    teacher_id = fields.Many2one(related="session_ids.teacher_id")
    teacher_color = fields.Integer(related="teacher_id.color")

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
