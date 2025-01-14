# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Education Course Pack",
    "summary": "Manage course pack",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "category": "education",
    "sequence": 1,
    "complexity": "easy",
    "author": "PESOL, Odoo Community Association (OCA)",
    "depends": ["education"],
    "data": [
        "views/course_view.xml",
        "views/enrollment_view.xml",
        "views/record_view.xml",
    ],
    "installable": True,
}
