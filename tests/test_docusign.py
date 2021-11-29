import json
import os
from datetime import timedelta
from random import randint

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

# Create your tests here.
from los_docusign.models import (
    DocusignChoiceConfig,
    DocusignEnvelopeStageData,
    DocusignOrgTemplate,
    DocusignTemplate,
    DocuSignUserAuth,
)
from los_docusign.utils.client import DocuSignClient
from los_docusign.utils.docusign_helper import (
    get_access_token,
    get_docusign_user,
    populate_text_tabs,
)


class TestCase(TestCase):
    def setUp(self):
        print("Inside setUp")
        content_type = ContentType.objects.get(model="organization")
        # ticket_content_type = ContentType.objects.get(model='ticket')
        ContentType.objects.create(model="etran", app_label="los_docusign")
        dcc = DocusignChoiceConfig.objects.get_or_create(
            config_key="3508S", docusign_model="docusign_templates"
        )
        DocuSignUserAuth.objects.create(
            access_token="wqerqwerqwerwqerqwererqwrwe",
            expires_at=timezone.now() - timedelta(days=1),
            organization_pk=2,
            organization_model=content_type,
            two_factor_enabled_flag=False,
            docusign_api_username="1820e571-f4c2-4e89-85b5-83953a845a2a",
            default_user=True,
        )
        with open(settings.BASE_DIR.joinpath("Envelope_3508S_DF.txt"), "r") as file:
            payload_3508S = file.read()
        docusign_template = DocusignTemplate.objects.create(
            docusign_payload=payload_3508S, template_type=dcc[0]
        )
        DocusignOrgTemplate.objects.create(
            organization_model=content_type,
            organization_pk=2,
            docusign_template=docusign_template,
        )
        # DocusignEnvelopeStageData.objects.create(slug="fa27a93e-a03a-42a0-8c10-dde6aabf454b",envelope_id="fa27a93e-a03a-42a0-8c10-dde6aabf454b",record_status="S",envelope_status="completed",created_at=timezone.now(),updated_at=timezone.now(),docusign_user=1,client_user_id=123456789,content_type=1,object_pk=1)
        self.field_dict = self.create_field_dict()

    def create_field_dict(self):
        return {
            "asian": "X",
            "hawaiian": "X",
            "black": "X",
            "not-hispanic": "X",
            "male": "X",
            "race-not-disclosed": "X",
            "hispanic": "X",
            "non-veteran": "X",
            "veteran": "X",
            "service-disabled-veteran": "X",
            "spouse-of-veteran": "X",
            "gender-not-disclosed": "X",
            "female": "X",
            "veteran-not-disclosed": "X",
            "borrower-address-2": "Address-2",
            "borrower-address-1": "Address-2",
            "borrower-name": "Borrower Name",
            "business-tin": "123456789",
            "ppp-first-draw-checkbox": "True",
            "ppp-loan-increase-amount": "1000.00",
            "authority-name": "Authority Name",
            "employee-count-loan-app": "1",
            "employee-count-forgiveness-app": "100",
            "ppp-loan-increase-date": "2021-08-20",
            "calculated-forgiveness-amount": "65000.00",
            "white": "X",
            "authority-title": "President",
            "american-indian": "X",
            "borrower-naics-code": "111212",
            "dba-name": "Test DBA Name",
            "ppp-second-draw-checkbox": "False",
            "principal-name": "Principal Name",
            "principal-position": "CEO",
            "ethnicity-not-disclosed": "X",
            "business-phone-no": "123456789",
            "covered-period-from-date": "2021-08-20",
            "payroll-cost": "90.60",
            "covered-period-to-date": "2021-10-20",
            "lender-loan-number": "123456789",
            "authority-email": "tejas@thesummitgrp.com",
            "loan-disbursement-date": "2021-08-21",
            "loan-amount": "9000.00",
            "sba-loan-number": "123456789",
        }

    def test_docusign(self):

        # envelope = DocusignEnvelopeStageData.objects.get(envelope_id="fa27a93e-a03a-42a0-8c10-dde6aabf454b")
        # create_and_generate_docusign(envelope, None)

        docusign_envelope_stage_data = DocusignEnvelopeStageData()

        organization_pk = "2"
        docusign_user = get_docusign_user(organization_pk)
        access_token = get_access_token(docusign_user)
        # print(f'access_token: {access_token}')
        docusign_envelope_stage_data.docusign_user = docusign_user
        docusign_envelope_stage_data.object_pk = 1
        docusign_envelope_stage_data.content_type = ContentType.objects.get(
            model="etran"
        )

        docusign_payload = None
        try:
            docusign_template = DocusignOrgTemplate.objects.get(
                organization_model=ContentType.objects.get(model="organization"),
                organization_pk=organization_pk,
                docusign_template__template_type__config_key="3508S",
            ).docusign_template
        except DocusignOrgTemplate.DoesNotExists as e:
            dsua = DocuSignUserAuth.objects.get(default_user=True)
            docusign_template = DocusignOrgTemplate.objects.get(
                organization=dsua.organization,
                docusign_template__template_type=DocusignChoiceConfig.DOCUSIGN_TEMPLATE,
            ).docusign_template

        docusign_payload = docusign_template.docusign_payload
        if docusign_payload is None:
            print("Payload Not found for org. Check database..return")
            return

        docusign_envelope_stage_data.template = docusign_template
        request_payload = json.loads(docusign_payload)

        # if self.organization.enable_wet_signature:
        #    resp['enableWetSign'] = True
        # print(docusign_payload)
        client_user_id = str(self.id) + str(randint(10000, 99999))
        docusign_envelope_stage_data.client_user_id = client_user_id
        signers = request_payload["recipients"]["signers"]
        emails = []

        for signer in signers:
            textTabs = signer["tabs"]["textTabs"]
            # print(json.loads(textTabs))
            populate_text_tabs(textTabs, text_tabs_data=self.field_dict)
            docusign_email_body = "Thank you for your continued business, please contact us directly for any questions going forward. "
            signer["email"] = "tejas@thesummitgrp.com"
            signer["name"] = "Tejas Bhandari"
            signer["clientUserId"] = client_user_id
            signer["emailNotification"]["emailBody"] = docusign_email_body
            if docusign_user.two_factor_enabled_flag:
                signer["idCheckConfigurationName"] = "Phone Auth $"
                signer["phoneAuthentication"]["recordVoicePrint"] = False
                signer["phoneAuthentication"]["validateRecipProvidedNumber"] = False
                signer["phoneAuthentication"]["recipMayProvideNumber"] = False
                signer["phoneAuthentication"]["senderProvidedNumbers"] = [
                    self.phone_number
                ]
            else:
                # del signer['idCheckConfigurationName']
                # del signer['phoneAuthentication']
                pass
            emails.append("tejas@thesummitgrp.com")
        docusign_envelope_stage_data.emails = emails

        # file1 = open("Envelope_debug.txt","w")
        # file1.write(json.dumps(resp))
        # file1.close()
        # return

        docusign_client = DocuSignClient(access_token=access_token)
        envelope_result = docusign_client.create_envelope(request_payload)

        # print(resp)
        resp = json.loads(envelope_result.text)
        print(resp)
        preview_data = {}
        preview_data["envelope_id"] = resp["envelopeId"]
        preview_data["authenticationMethod"] = "None"
        preview_data["email"] = "tejas@thesummitgrp.com"
        preview_data["userName"] = "Tejas Bhandari"
        preview_data["clientUserId"] = client_user_id
        preview_data["returnUrl"] = "http://www.google.com"

        preview_result = docusign_client.generate_docusign_preview_url(preview_data)
        print(preview_result.text)
        docusign_envelope_stage_data.envelope_response = envelope_result.text
        current_time = timezone.now()
        if envelope_result.status_code == 201:
            docusign_envelope_stage_data.record_status = "S"
            docusign_envelope_stage_data.envelope_id = resp["envelopeId"]
            docusign_envelope_stage_data.envelope_status = resp["status"]
            docusign_envelope_stage_data.created_date = current_time
            docusign_envelope_stage_data.updated_date = current_time
        else:
            docusign_envelope_stage_data.record_status = "F"
            docusign_envelope_stage_data.error_message = envelope_result.text
            # TODO: Set some error message received from the response
            docusign_envelope_stage_data.created_date = current_time
            docusign_envelope_stage_data.updated_date = current_time

            # sentry_sdk.capture_exception(Exception(description_of_error))

        docusign_envelope_stage_data.save()

        print(
            DocusignEnvelopeStageData.objects.filter(
                envelope_id=docusign_envelope_stage_data.envelope_id
            ).values()
        )

        # Testing Webhook notification processing
        with open(f"{os.getcwd()}/tests/test_webhook.xml", "r") as file:
            data = (
                file.read()
                .replace("\n", "")
                .replace(
                    "<EnvelopeID></EnvelopeID>",
                    f"<EnvelopeID>{resp['envelopeId']}</EnvelopeID>",
                )
            )

        envelopeId, envelope_status = docusign_client.process_docusign_notification(
            data
        )
        self.assertEqual(envelope_status, "completed")
        self.assertEqual(envelopeId, resp["envelopeId"])
        if envelope_status == "completed":
            input_data = {}
            input_data["envelope_id"] = "6aaec95f-bc54-48cf-8270-5b27fe5e41d8"
            input_data["doc_download_option"] = "combined"
            result = docusign_client.download_docusign_document(input_data)
            self.assertEqual(result.status_code, 200)
