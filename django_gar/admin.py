from django.contrib import admin
from django.shortcuts import get_object_or_404

from .gar import delete_gar_subscription, get_gar_subscription
from .forms import GARInstitutionForm
from .models import GARInstitution


class GARInstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "project_code")
    form = GARInstitutionForm

    def delete_model(self, request, obj):
        delete_gar_subscription(obj.subscription_id)
        super().delete_model(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = get_object_or_404(self.get_queryset(request), pk=object_id)
        extra_context = extra_context or {}
        gar_subscription = get_gar_subscription(obj.uai, obj.subscription_id)
        if gar_subscription:
            extra_context["gar_subscription"] = gar_subscription
        else:
            extra_context["gar_subscription"] = (
                "L'abonnement n'existe pas dans le GAR. "
                "Vous pouvez le supprimer et en créer un nouveau."
            )
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(GARInstitution, GARInstitutionAdmin)
