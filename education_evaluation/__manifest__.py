# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Education Evaluation",
    "summary": "Education Exam for Odoo",
    "version": "11.0.1.0.1",
    "category": "Education",
    "website": "https://github.com/OCA/vertical_education",
    "author": "PESOL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": ["base", "education", "mail"],
    "data": [
        "data/education_exam_multicompany.xml",
        "data/education_result_multicompany.xml",
        "views/course_view.xml",
        "views/exam_view.xml",
        "views/result_view.xml",
        "views/record_view.xml",
        "views/student_view.xml",
        "views/grading_view.xml",
        "security/evaluation_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/education_grading_scale_demo.xml",
        "demo/education_exam_demo.xml",
    ],
}
