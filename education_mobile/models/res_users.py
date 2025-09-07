from odoo import fields, models


class User(models.Model):
    _inherit = "res.users"

    fcm_token_ids = fields.One2many("fcm.token", "user_id", "FCM Token")
