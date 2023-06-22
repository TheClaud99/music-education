# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Education",
    "summary": "Education Management for Odoo",
    "version": "16.0.1.0.0",
    "category": "Education",
    "website": "https://pesol.es",
    "author": "PESOL",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": ["base", "mail"],
    "data": [
        "security/education_security.xml",
        "security/ir.model.access.csv",
        "views/menu_view.xml",
        "views/course_view.xml",
        "views/course_category_view.xml",
        "views/subject_view.xml",
        "views/enrollment_view.xml",
        "views/group_view.xml",
        "views/partner_view.xml",
    ],
    "demo": [
        "demo/education_res_partner_demo.xml",
        "demo/education_subject_demo.xml",
        "demo/education_teacher_demo.xml",
        "demo/education_student_demo.xml",
        "demo/education_course_demo.xml",
        "demo/education_group_demo.xml",
        "demo/education_enrollment_demo.xml",
    ],
}
