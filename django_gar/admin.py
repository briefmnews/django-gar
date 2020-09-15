from django.contrib import admin

from .gar import delete_gar_subscription
from .forms import GARInstitutionForm
from .models import GARInstitution


class GARInstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai")
    form = GARInstitutionForm

    def delete_model(self, request, obj):
        delete_gar_subscription(obj.subscription_id)
        super().delete_model(request, obj)


admin.site.register(GARInstitution, GARInstitutionAdmin)
