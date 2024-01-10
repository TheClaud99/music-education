from odoo import _, api, fields, models


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
        default=lambda self: self.env.company_id.id,
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
        return super().create(vals)


class EducationCourseCategory(models.Model):
    _name = "education.course.category"
    _description = "Course Category"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _rec_name = "complete_name"
    _order = "name"

    name = fields.Char(string="Name", index=True, required=True, translate=True)
    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
    parent_id = fields.Many2one(
        comodel_name="education.course.category",
        string="Parent Category",
        index=True,
        ondelete="cascade",
    )
    child_id = fields.One2many(
        comodel_name="education.course.category",
        inverse_name="parent_id",
        string="Child Categories",
    )
    parent_path = fields.Char(index=True, unaccent=False)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = "%s / %s" % (
                    category.parent_id.complete_name,
                    category.name,
                )
            else:
                category.complete_name = category.name


class EducationSubject(models.Model):
    _name = "education.subject"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=True)

    course_ids = fields.One2many(
        comodel_name="education.course.subject",
        inverse_name="subject_id",
        string="Courses",
    )


class EducationCourseSubject(models.Model):
    _name = "education.course.subject"
    _rec_name = "subject_id"

    course_id = fields.Many2one(comodel_name="education.course", string="Course")
    subject_id = fields.Many2one(comodel_name="education.subject", string="Subject")


class EducationInstrument(models.Model):
    _name = "education.instrument"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=True)

    course_ids = fields.One2many(
        comodel_name="education.course",
        inverse_name="instrument_id",
        string="Courses",
    )


class EducationCourse(models.Model):
    _name = "education.course"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one(
        comodel_name="education.course.category", string="Category"
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    duration = fields.Float(string="Duration", company_dependent=True)
    active = fields.Boolean(string="Active", default=True)
    instrument_id = fields.Many2one("education.instrument", "Strumento")
    teacher_id = fields.Many2one("res.partner", "Insegnante")

    enrollment_ids = fields.One2many("education.enrollment", "course_id", "Iscrizioni")
    students = fields.Many2many(
        "res.partner", "education_enrollment", "course_id", "student_id", "Studenti"
    )
