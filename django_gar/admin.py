import csv

from django.urls import path
from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.html import format_html

from .gar import get_gar_subscription, get_allocations
from .forms import GARInstitutionForm
from .models import GARInstitution

GAR_RESOURCES_ID = getattr(settings, "GAR_RESOURCES_ID", "")


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
    change_list_template = "admin/django_gar/change_list.html"

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

    def get_urls(self):
        urlpatterns = super().get_urls()

        allocations_report_url = [
            path(
                "allocations-report/generate/",
                self.admin_site.admin_view(self.allocations_report),
                name="{app_label}_{model_name}_generate_allocations_report".format(
                    app_label=self.model._meta.app_label,
                    model_name=self.model._meta.model_name,
                ),
            )
        ]

        return allocations_report_url + urlpatterns

    def allocations_report(self, request):
        project_code = request.GET.get("project_code")

        if not project_code:
            messages.success(
                request,
                "Impossible de télécharger le rapport d’affectations, le code projet ressource est introuvable",
            )
            return redirect(
                reverse(
                    "admin:{}_{}_changelist".format(
                        self.model._meta.app_label, self.model._meta.model_name
                    )
                )
            )

        allocations_response = get_allocations(project_code=project_code)
        data = allocations_response.content.decode("utf-8")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="rapport_affectations_{project_code}.csv"'
        )

        writer = csv.writer(response)
        rows = [line.split(";") for line in data.splitlines()]

        filtered_rows = [["InstitutionName"] + rows[0]]

        gar_institutions = self.model.objects.filter(project_code=project_code)

        filtered_rows += [
            [
                (
                    gar_institutions.get(uai=row[0]).institution_name
                    if gar_institutions.filter(uai=row[0]).exists()
                    else "-"
                )
            ]
            + row
            for row in rows[1:]
            if settings.GAR_RESOURCES_ID in row
        ]

        # Add institutions with no affectations
        existing_uais = {row[1] for row in filtered_rows[1:]}

        filtered_rows += [
            [
                gar_institution.institution_name,
                gar_institution.uai,
                gar_institution.subscription_id,
                project_code,
                settings.GAR_RESOURCES_ID,
                0,
                0,
                0,
                0,
            ]
            for gar_institution in gar_institutions
            if gar_institution.uai not in existing_uais
        ]

        writer.writerows(filtered_rows)

        return response
