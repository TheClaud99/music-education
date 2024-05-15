# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    education_product_id = fields.Many2one(
        "product.product",
        string="Default Education Product",
        related="company_id.education_product_id",
        readonly=False,
    )
