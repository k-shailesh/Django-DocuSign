from django.contrib import admin

from .models import Organization


# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    list_display = ("name", "city", "web", "loan_mod_request_host_name")
    search_fields = ("name",)
