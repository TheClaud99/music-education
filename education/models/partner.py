from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    teacher = fields.Boolean(string="Teacher")
    student = fields.Boolean(string="Student")

    enrollment_ids = fields.One2many("education.enrollment", "student_id", "Iscrizioni")
    courses = fields.Many2many(
        "education.course", "education_enrollment", "student_id", "course_id", "Corsi"
    )

    def open_student_enrollments(self):
        return {
            "name": _("Enrollments"),
            "view_mode": "tree,form",
            "res_model": "education.enrollment",
            "src_model": "res.partner",
            "type": "ir.actions.act_window",
            "domain": '[("student_id", "=", active_id)]',
        }
