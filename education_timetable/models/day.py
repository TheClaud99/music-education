from odoo import fields, models


class EducationDay(models.Model):
    _name = "education.day"
    _description = "Giorno della settimana"

    name = fields.Char()
    code = fields.Integer()
