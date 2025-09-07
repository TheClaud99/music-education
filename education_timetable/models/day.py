from odoo import fields, models


class EducationDay(models.Model):
    _name = "education.day"

    name = fields.Char()
    code = fields.Integer()
