from django.contrib import admin
from django.utils.safestring import mark_safe

from .gar import get_gar_subscription
from .forms import GARInstitutionForm
from .models import GARInstitution

@admin.register(GARInstitution)
class GARInstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    readonly_fields = ("id_ent", "gar_subscription_response")
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "project_code")
    list_filter = ["project_code"]
    form = GARInstitutionForm

    @admin.display(description="Etat de l'abonnement dans le GAR")
    def gar_subscription_response(self, obj):
        gar_subscription = get_gar_subscription(obj.uai, obj.subscription_id)

        if not gar_subscription:
            return (
                "L'abonnement n'existe pas dans le GAR. "
                "Vous pouvez le supprimer et en créer un nouveau."
            )

        response = ""
        for element in gar_subscription.find_all():
            response += f"{element.name} : {element.text}<br/>"

        return mark_safe(f"<code>{response}</code>")
