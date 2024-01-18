from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    attendance_ids = fields.One2many(
        comodel_name="education.session.attendance",
        inverse_name="student_id",
        string="Presenze",
    )

    session_ids = fields.One2many(
        comodel_name="education.session", inverse_name="teacher_id", string="Sessions"
    )
