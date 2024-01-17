from odoo import api, fields, models


class EducationSessionPresence(models.TransientModel):
    _name = "education.session.presence"

    session_id = fields.Many2one(comodel_name="education.session", string="Session")

    session_presence_ids = fields.One2many(
        comodel_name="education.session.presence.line",
        inverse_name="presence_id",
        string="Session Presence",
    )

    @api.onchange("session_id")
    def _onchange_session_students(self):
        lines = []
        enrollments = self.session_id.timetable_id.group_id.enrollment_ids
        for enroll in enrollments.filtered(lambda e: e.state == "done"):
            lines.append((0, 0, {"student_id": enroll.student_id.id}))
        self.session_presence_ids = lines

    def create_attendances(self):
        values = []
        self.ensure_one()
        students = self.session_id.attendance_ids.mapped("student_id")
        for line in self.session_presence_ids.filtered(lambda l: l.lack):
            if line.student_id not in students:
                attendance_values = {
                    "session_id": self.env.context.get("active_id"),
                    "student_id": line.student_id.id,
                    "notes": line.notes,
                }
                values.append((0, 0, attendance_values))
            else:
                self.session_id.attendance_ids.filtered(
                    lambda l: l.student_id == line.student_id
                ).write({"notes": line.notes})
        self.session_id.attendance_ids = values
        self.session_id.state = "done"
