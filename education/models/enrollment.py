from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationEnrollment(models.Model):
    _name = "education.enrollment"
    _inherit = ["mail.thread"]
    _rec_name = "code"
    _order = "enrollment_date desc"

    code = fields.Char(
        string="Code",
        default=lambda self: _("New"),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id.id,
        string="Company",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    student_id = fields.Many2one(
        comodel_name="res.partner",
        string="Student",
        required=True,
    )
    course_id = fields.Many2one(
        comodel_name="education.course",
        string="Course",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    teacher_id = fields.Many2one(related="course_id.teacher_id")
    group_id = fields.Many2one(
        comodel_name="education.group",
        string="Group",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    record_id = fields.Many2one(comodel_name="education.record", string="Record")
    enrollment_date = fields.Date(string="Enrollment Date")
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancel", "Cancelled")],
        string="Status",
        default="draft",
    )

    def action_draft(self):
        self.ensure_one()
        self.state = "draft"

    def action_cancel(self):
        self.ensure_one()
        self.state = "cancel"

    def set_done(self):
        self.enrollment_date = fields.Date.today()
        self.student_id.student = True
        self.state = "done"

    def action_done(self):
        self.set_done()

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get("code", "New") == "New":
                val["code"] = (
                    self.env["ir.sequence"].next_by_code("education.enrollment")
                    or "New"
                )
        return super(EducationEnrollment, self).create(vals)
