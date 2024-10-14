import csv

from django.contrib import admin
from django.utils.html import format_html

from .gar import get_gar_subscription, get_allocations
from .forms import GARInstitutionForm
from .models import GARInstitution


@admin.register(GARInstitution)
class GARInstitutionAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("institution_name", "user", "uai", "ends_at")
    list_select_related = ("user",)
    readonly_fields = ("id_ent", "gar_subscription_response", "get_allocations")
    ordering = ("institution_name",)
    search_fields = ("institution_name", "user__email", "uai", "project_code")
    list_filter = ["project_code"]
    form = GARInstitutionForm

    @admin.display(description="Etat de l'abonnement dans le GAR")
    def gar_subscription_response(self, obj):
        if not obj.uai:
            return ""

        gar_subscription = get_gar_subscription(obj.uai, obj.subscription_id)

        if not gar_subscription:
            return (
                "L'abonnement n'existe pas dans le GAR. "
                "Vous pouvez le supprimer et en créer un nouveau."
            )

        response = ""
        for element in gar_subscription.find_all():
            response += f"{element.name} : {element.text}<br/>"

        return format_html(f"<code>{response}</code>")

    @admin.display(description="Etat des affectations")
    def get_allocations(self, obj):
        if not obj.uai:
            return ""

        response = get_allocations(subscription_id=obj.subscription_id)
        decoded_response = response.content.decode("utf-8")

        if response.status_code == 200 and decoded_response:
            lines = decoded_response.splitlines()
            reader = csv.reader(lines, delimiter=";")
            rows = list(reader)
            headers = rows[0]
            values = rows[1]
            allocations = ""
            for header, value in zip(headers, values):
                allocations += f"{header} : {value}<br/>"
        elif response.status_code == 200:
            allocations = "L'établissement n'a pas encore affecté la ressource.<br/>Les informations fournies par le webservice font l’objet d’un traitement asynchrone et sont par conséquent actualisées quotidiennement. Il peut être constaté une latence dans la prise en compte de changements en cas d’affectations / récupérations de licences au sein d’une même journée."
        else:
            allocations = decoded_response.get("message")

        return format_html(f"<code>{allocations}</code>")
