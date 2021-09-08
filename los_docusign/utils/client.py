import json

from django.conf import settings

from .api_handler import ApiHandler


class DocuSignClient:
    def __init__(self,access_token: str):
        self.account_id = settings.DOCUSIGN_API_ACCOUNT_ID
        self.api_key = f'Bearer {access_token}'

    # def generate_docusign_preview_url(self, email, userName, client_user_id, returnUrl, envelope_id, access_token, authenticationMethod=None):
    def generate_docusign_preview_url(self, params: dict):
        envelope_id = params["envelope_id"]
        authentication_method = params["authenticationMethod"]
        email = params["email"]
        user_name = params["userName"]
        client_user_id = params["clientUserId"]
        return_url = params["returnUrl"]
        access_token = params["access_token"]

        url = settings.DOCUSIGN_API_ENDPOINT

        preview_resource_path = (
            f"{self.account_id}/envelopes/{envelope_id}/views/recipient"
        )
        preview_url = url + preview_resource_path
        preview_data = {
            "authenticationMethod": authentication_method,
            "email": email,
            "userName": user_name,
            "clientUserId": client_user_id,
            "returnUrl": return_url,
        }
        docusign_handler = ApiHandler(preview_url, access_token)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(preview_data)
        )
        return envelope_result

    def create_envelope(self, payload):

        url = settings.DOCUSIGN_API_ENDPOINT

        resource_path = self.account_id + "/envelopes"
        envelope_url = url + resource_path
        docusign_handler = ApiHandler(envelope_url, self.api_key)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(payload)
        )
        return envelope_result
