from odoo import fields, models


class EducationSessionPresenceLine(models.TransientModel):
    _name = "education.session.presence.line"

    presence_id = fields.Many2one(
        comodel_name="education.session.presence", string="Session Presence"
    )

    student_id = fields.Many2one(comodel_name="res.partner", string="Student")

    lack = fields.Boolean()

    notes = fields.Char()
