from odoo import api, fields, models


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
