import os

import google.auth.transport.requests
import requests
from google.oauth2 import service_account

from odoo import api, fields, models
from odoo.modules import get_module_path

# Percorso al file della service account JSON scaricato da Firebase
SERVICE_ACCOUNT_FILE = os.path.join(
    get_module_path("education_mobile"), "firebase-adminsdk.json"
)


class FcmToken(models.Model):
    """Using this class create the registration id for the user to send
    push notifications"""

    _name = "fcm.token"
    _description = "Firebase Cloud Messaging Token"

    user_id = fields.Many2one(
        "res.users",
        "Firebase User",
        help="Corresponding Firebase User",
        readonly=True,
        required=True,
        index=True,
        default=lambda self: self.env.user,
    )
    token = fields.Char(
        "FCM Token",
        help="Firebase Registration Token",
        readonly=True,
        required=True,
        index=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "unique_token",
            "UNIQUE(token)",
            "Only one token can exist.",
        ),
    ]

    @api.model
    def register_token(self, token):
        """
        Method called by the mobile application on user login
        """
        if not token:
            raise ValueError("FCM token cannot be null")
        rec = self.search([("token", "=", token)])
        if not rec:
            rec = self.create({"token": token})
        return rec.id

    @api.model
    def _get_access_token(self):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"],
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token, credentials.project_id

    def send_fcm_notification(self, title: str, body: str, data: dict | None = None):
        access_token, project_id = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8",
        }
        payload = {
            "message": {
                "token": self.token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "data": data or {},
            }
        }
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        return response.json()
