from odoo import _, api, fields, models


class EducationSessionAttendance(models.Model):
    _name = "education.session.attendance"
    _inherit = ["mail.thread"]

    name = fields.Char(
        compute="_compute_name",
        store=False,
        readonly=True,
        copy=False,
    )

    session_id = fields.Many2one(
        comodel_name="education.session",
        string="Lezione",
        required=True,
        index=True,
        ondelete="cascade",
    )

    course_id = fields.Many2one(related="session_id.timetable_id.course_id")
    student_id = fields.Many2one("res.partner", "Studente", required=True)
    is_paid = fields.Boolean(copy=False, tracking=True)

    notes = fields.Char(string="Note")

    supporting_document = fields.Boolean()

    start = fields.Datetime("Start time", related="session_id.start")

    def set_paid(self):
        self.write({"is_paid": True})
        return {}

    def set_unpaid(self):
        return self.write({"is_paid": False})

    @api.depends("student_id", "session_id.start")
    def _compute_name(self):
        for attendance in self:
            attendance.name = _("{} - {}").format(
                attendance.start, attendance.student_id.name
            )
