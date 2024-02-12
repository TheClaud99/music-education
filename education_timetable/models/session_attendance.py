from odoo import fields, models


class EducationSessionAttendance(models.Model):
    _name = "education.session.attendance"
    _inherit = ["mail.thread"]

    session_id = fields.Many2one(
        comodel_name="education.session",
        string="Lezione",
        required=True,
        index=True,
        ondelete="cascade",
    )

    student_id = fields.Many2one(comodel_name="res.partner", string="Studente")
    is_paid = fields.Boolean("Is Paid", copy=False, tracking=True)

    notes = fields.Char(string="Note")

    supporting_document = fields.Boolean(string="Supporting Document")

    def set_paid(self):
        self.write({"is_paid": True})
        return {}
