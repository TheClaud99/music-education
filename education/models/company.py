# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "mail.thread"]

    education_product_id = fields.Many2one(
        "product.product", string="Default product for education"
    )
