# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
#                Luis Adan Jimenez Hernandez <luis.jimenez@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

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
    is_paid = fields.Boolean("Is Paid", copy=False)

    notes = fields.Char(string="Note")

    supporting_document = fields.Boolean(string="Supporting Document")
