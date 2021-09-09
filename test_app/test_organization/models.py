import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def organization_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/organization/organization_slug/files/slug/<filename>
    return "organization/{0}/files/{1}".format(instance.slug, filename)


def public_organization_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/public/organization_slug/slug/<filename>
    return "public/{0}/{1}".format(instance.slug, filename)


class Organization(models.Model):
    class Meta:
        db_table = "organizations"
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    BANK = "BA"
    CREDITUNION = "CU"
    THRIFT = "TH"
    QUALIFIEDINVESTOR = "QI"
    OTHER = "OT"
    NONE = "NO"
    ORGANIZATION_TYPE_CHOICES = (
        (BANK, "Bank"),
        (CREDITUNION, "Credit Union"),
        (THRIFT, "Thrift"),
        (QUALIFIEDINVESTOR, "Qualified Investor"),
        (OTHER, "Other"),
    )
    FDIC = "FD"
    OCC = "OC"
    RATING_AGENCY_CHOICES = (
        (FDIC, "FDIC"),
        (OCC, "OCC"),
        (OTHER, "Other"),
        (NONE, "None"),
    )

    DAY_COUNT_METHOD_CHOICES = (
        ("actual360", "Actual/360"),
        ("actual365", "Actual/365"),
        # ('actualactual', 'Actual/Actual'),
        ("thirty360", "30/360"),
    )

    LOAN_NUMBER_ASSIGNMENT_STRATEGY_CHOOSE_FROM_POOL = "choose-from-pool"
    LOAN_NUMBER_ASSIGNMENT_STRATEGY_DEFER_TO_ORG = "defer-to-org"

    LOAN_NUMBER_ASSIGNMENT_STRATEGY_CHOICES = (
        (LOAN_NUMBER_ASSIGNMENT_STRATEGY_CHOOSE_FROM_POOL, "Choose From Pool"),
        (LOAN_NUMBER_ASSIGNMENT_STRATEGY_DEFER_TO_ORG, "Defer to Organization"),
    )

    slug = models.UUIDField(
        default=uuid.uuid4, blank=True, editable=False, db_index=True
    )
    name = models.CharField("Organization Name", max_length=200)
    organization_type = models.CharField(
        "Organization Type",
        max_length=2,
        choices=ORGANIZATION_TYPE_CHOICES,
        default=BANK,
    )
    description = models.TextField("Description", blank=True, null=True)
    street_address = models.CharField("Address Line 1", max_length=200, blank=True)
    street_address2 = models.CharField("Address Line 2", max_length=200, blank=True)
    city = models.CharField("City", max_length=200, blank=True)

    web = models.URLField("Website URL", max_length=200, blank=True)
    created_at = models.DateTimeField(
        auto_created=True, auto_now_add=True, editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    lender = models.BooleanField("Organization is a Lender?", default=False)
    buyer = models.BooleanField("Organization is a loan buyer?", default=False)
    primary_contact_first_name = models.CharField(
        "Primary Contact First Name", null=True, blank=True, max_length=125
    )
    primary_contact_last_name = models.CharField(
        "Primary Contact Last Name", null=True, blank=True, max_length=125
    )
    primary_contact_email = models.EmailField(
        "Primary Contact Email", null=True, blank=True
    )
    primary_contact_phone = models.CharField(
        "Primary Contact Phone Number", null=True, blank=True, max_length=128
    )
    primary_contact_cell_phone = models.CharField(
        "Primary Contact Cell Phone Number", null=True, blank=True, max_length=128
    )
    primary_contact_title = models.CharField(max_length=64, null=True, blank=True)
    require_two_factor = models.BooleanField(
        "Require Two Factor Authentication", default=False
    )
    date_established = models.IntegerField("Date Established", blank=True, null=True)
    federal_reserve_id = models.IntegerField(
        "Federal Reserve ID", blank=True, null=True
    )
    fdic_cert_number = models.IntegerField(
        "FDIC Certificate Number", blank=True, null=True
    )
    rating_agency = models.CharField(
        "Rating Agency", max_length=2, choices=RATING_AGENCY_CHOICES, default=NONE
    )
    swift_bic = models.CharField("SWIFT/BIC", max_length=15, blank=True, null=True)
    logo = models.FileField(
        "Logo",
        upload_to=public_organization_file_path,
        max_length=255,
        null=True,
        blank=True,
    )
    privacy_policy_url = models.URLField(
        "Privacy Policy URL", max_length=200, blank=True
    )
    terms_of_service_url = models.URLField(
        "Terms of Service URL", max_length=200, blank=True
    )
    enable_loan_mod_request_screen = models.BooleanField(
        "Enable Loan Modification Request Screen", default=False
    )
    loan_mod_request_host_name = models.CharField(
        "CNAME", blank=True, null=True, max_length=30, unique=True
    )
    custom_loan_mod_request_text = models.TextField(
        "Custom text for loan modification public page", blank=True, null=True
    )
    google_analytics_id = models.CharField(
        "Google Analytics ID", max_length=50, blank=True, null=True
    )
    require_queue_user_membership = models.BooleanField(
        "Require user to be specifically assigned to this queue in order to view tickets",
        default=False,
        help_text="This will restrict users from viewing this queue if they are not assigned to this queue specifically",
    )
    custom_footer = models.TextField(
        "Custom footer for public pages", blank=True, null=True
    )
    custom_email_text = models.TextField(
        "Custom text for use in email templates", blank=True, null=True
    )
    ppp_forgiveness_instructions = models.TextField(
        "HTML for PPP Forgiveness Instructions Tab", blank=True, null=True
    )
    docusign_enabled = models.BooleanField("Docusign Enabled?", default=False)
    chatlio_enabled = models.BooleanField("Chatlio Enabled?", default=False)
    session_timeout = models.IntegerField("Session timeout (in seconds)", default=3600)
    enable_2019_annual_revenue_input = models.BooleanField(
        "Enable Borrower Input of 2020 Annual Revenue", default=False
    )
    get_started_background_image = models.FileField(
        "Image on Get Started Page",
        upload_to=public_organization_file_path,
        max_length=255,
        null=True,
        blank=True,
    )
    get_started_header_text = models.CharField(
        "Get Started Page Header Text", blank=True, null=True, max_length=255
    )
    get_started_description_text = models.CharField(
        "Get Started Page Description Text", blank=True, null=True, max_length=255
    )
    show_banker_contact_info = models.BooleanField(
        "Show Banker Contact Info to Borrower (when able)", default=True
    )
    show_banker_contact_info = models.BooleanField(
        "Show Banker Contact Info to Borrower (when able)", default=True
    )
    sba_product_token = models.CharField(
        "SBA API Key", blank=True, null=True, max_length=255
    )
    forgiveness_enabled = models.BooleanField(default=True)
    origination_enabled = models.BooleanField(default=False)
    origination_allow_banker_selection = models.BooleanField(
        "Origination - Allow Borrower to Select their Banker", default=True
    )
    origination_documents_required = models.BooleanField(
        "Origination - Borrower Supporting Documents are Required", default=True
    )
    day_count_method = models.CharField(
        "Interest calculation method",
        max_length=50,
        choices=DAY_COUNT_METHOD_CHOICES,
        default="actual360",
    )
    sba_location_id = models.CharField(
        "SBA Location ID", max_length=15, blank=True, null=True
    )
    loan_number_assignment_strategy = models.CharField(
        max_length=125,
        choices=LOAN_NUMBER_ASSIGNMENT_STRATEGY_CHOICES,
        default=LOAN_NUMBER_ASSIGNMENT_STRATEGY_DEFER_TO_ORG,
    )
    orig_only_existing_customers = models.BooleanField(
        "Only Allow Existing Customers for Origination",
        default=False,
        help_text="Only allows existing Bank customers to go through Origination",
    )
    enable_wet_signature = models.BooleanField(default=False)
    is_docusign_preview_enabled = models.BooleanField(default=False)
    is_kyc_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({str(self.city)})"

    @property
    def safe_name(self):
        """
        Removes characters from the organization's name that may cause file/url path issues
        """
        if not self.name:
            return

        invalid_chars = dict.fromkeys("/?><:\"\\|*'")
        trans_table = str.maketrans(invalid_chars)

        return self.name.translate(trans_table)
