import logging
from datetime import timedelta
from os import path

from django.conf import settings

# import sentry_sdk
from django.utils import timezone
from docusign_esign import ApiClient
from docusign_esign.client.api_exception import ApiException

from los_docusign.models import DocusignOrgTemplate, DocuSignUserAuth

SCOPES = ["signature"]

logger = logging.getLogger(__name__)


def get_docusign_user(organization_pk):
    try:
        # Try if the user is the available and has the docusign account
        docusign_user = DocuSignUserAuth.objects.get(organization_pk=organization_pk)
    except DocuSignUserAuth.DoesNotExist:
        # Else use the admin user
        # Tejas, isn't default_user supposed to be the default user we use as a
        # fallback?
        docusign_user = DocuSignUserAuth.objects.get(default_user=True)

    return docusign_user


def get_access_token(docusign_user):
    docusign_token_expiry = settings.DOCUSIGN_TOKEN_EXPIRY_IN_SECONDS

    if docusign_user.expires_at >= timezone.now():
        access_token = docusign_user.access_token
    else:
        token_response = _jwt_auth(docusign_user.docusign_api_username)
        access_token = token_response.access_token
        docusign_user.access_token = access_token
        docusign_user.expires_at = timezone.now() + timedelta(
            seconds=int(docusign_token_expiry)
        )
        docusign_user.save()

    return access_token


def check_docusign_access_token(organization_pk):
    docusign_user = get_docusign_user(organization_pk)
    token_response = _jwt_auth(docusign_user.docusign_api_username)
    if not token_response:
        use_scopes = SCOPES
        if "impersonation" not in use_scopes:
            use_scopes.append("impersonation")
        consent_scopes = " ".join(use_scopes)
        redirect_uri = settings.DOCUSIGN_REDIRECT_APP_URL
        consent_url = (
            f"https://{settings.DOCUSIGN_AUTHORIZATION_SERVER}/oauth/auth?response_type=code&"
            f"scope={consent_scopes}&client_id={settings.DOCUSIGN_CLIENT_ID}&redirect_uri={redirect_uri}"
        )
        return consent_url
    return None


def _jwt_auth(docusign_api_username):
    """JSON Web Token authorization"""
    api_client = ApiClient()
    api_client.set_base_path(settings.DOCUSIGN_AUTHORIZATION_SERVER)
    use_scopes = SCOPES
    if "impersonation" not in use_scopes:
        use_scopes.append("impersonation")

    # Catch IO error
    try:
        private_key = _get_private_key().encode("ascii").decode("utf-8")

    except (OSError, IOError) as err:
        # sentry_sdk.capture_exception(Exception(f'OSError, IOError in Docusign JWT Auth'))
        return "error"

    try:
        jwtTokenResponse = api_client.request_jwt_user_token(
            client_id=str(settings.DOCUSIGN_CLIENT_ID),
            user_id=docusign_api_username,
            oauth_host_name=str(settings.DOCUSIGN_AUTHORIZATION_SERVER),
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=use_scopes,
        )
    except ApiException as err:

        body = err.body.decode("utf8")
        # Grand explicit consent for the application
        if "consent_required" in body:
            return None
        else:
            # sentry_sdk.capture_exception(err)
            raise Exception

    return jwtTokenResponse


def _get_private_key():
    """
    Check that the private key present in the file and if it is, get it from the file.
    In the opposite way get it from config variable.
    """
    private_key_file = path.abspath(settings.DOCUSIGN_PRIVATE_KEY_FILE)
    if path.isfile(private_key_file):
        with open(private_key_file) as private_key_file:
            private_key = private_key_file.read()
    else:
        private_key = settings.DOCUSIGN_PRIVATE_KEY_FILE.encode().decode(
            "unicode-escape"
        )

    return private_key


def populate_text_tabs(text_tabs_forms, text_tabs_data: dict):
    # Need to populate all the text tabs with the values
    for textTabsInfo in text_tabs_forms:
        tab_label = textTabsInfo["tabLabel"]
        try:
            textTabsInfo["value"] = text_tabs_data.get(tab_label)
        except KeyError as e:
            print(f"Key not found {e}")


def get_docusign_template(organization_pk, template_name=None):
    docusign_payload = None
    try:
        docusign_template = DocusignOrgTemplate.objects.get(
            organization_model="organization",
            docusign_template__template_type=template_name,
            organization_pk=organization_pk,
        ).docusign_template
    except DocusignOrgTemplate.DoesNotExist:
        dsua = DocuSignUserAuth.objects.get(default_user=True)
        docusign_template = DocusignOrgTemplate.objects.get(
            object_pk=dsua.object_pk, docusign_template__template_type=template_name
        ).docusign_template

    docusign_payload = docusign_template.docusign_payload
    if docusign_payload is None:
        print("Payload Not found for org. Check database..return")
        return

    # resp = json.loads(docusign_payload)
    return docusign_payload
