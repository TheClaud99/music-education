from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    attendance_ids = fields.One2many(
        comodel_name="education.session.attendance",
        inverse_name="student_id",
        string="Presenze",
    )

    attendances_to_pay_ids = fields.One2many(
        "education.session.attendance",
        "student_id",
        "Attendances to pay",
        domain=[("is_paid", "=", False)],
    )

    session_ids = fields.One2many(
        comodel_name="education.session", inverse_name="teacher_id", string="Sessions"
    )

    attendances_to_pay_count = fields.Integer(
        "# Attendances to pay", compute="_compute_attendances_to_pay_count"
    )

    def _compute_attendances_to_pay_count(self):
        for partner in self:
            partner.attendances_to_pay_count = len(self.attendances_to_pay_ids)

    def open_student_attendances(self):
        return {
            "name": _("Presenze"),
            "view_mode": "tree,form",
            "res_model": "education.session.attendance",
            "type": "ir.actions.act_window",
            "domain": [("student_id", "=", self.id)],
            "context": {"search_default_not_paid": True},
        }
