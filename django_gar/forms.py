import datetime
import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError

from .gar import (
    get_gar_certificate,
    get_gar_headers,
    get_gar_request_url,
)
from .models import GARInstitution

GAR_DISTRIBUTOR_ID = getattr(settings, "GAR_DISTRIBUTOR_ID", "")
GAR_RESOURCES_ID = getattr(settings, "GAR_RESOURCES_ID", "")
GAR_ORGANIZATION_NAME = getattr(settings, "GAR_ORGANIZATION_NAME", "")
GAR_SUBSCRIPTION_PREFIX = getattr(settings, "GAR_SUBSCRIPTION_PREFIX", "")
User = get_user_model()


class GARInstitutionForm(ModelForm):
    subscription_id = forms.CharField(
        widget=forms.TextInput(attrs={"readonly": "readonly"})
    )

    class Meta:
        model = GARInstitution
        fields = (
            "uai",
            "institution_name",
            "ends_at",
            "user",
            "project_code",
            "subscription_id",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subscription_id"].initial = "{}{}".format(
            GAR_SUBSCRIPTION_PREFIX, int(time.time())
        )

        # Disable ends_at field on update form
        instance = getattr(self, "instance", None)
        if instance.pk:
            self.fields["ends_at"].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        self._create_or_update_gar_subscription()
        return cleaned_data

    def clean_uai(self):
        return self.cleaned_data.get("uai").upper().strip()

    def _create_or_update_gar_subscription(self):
        """
        A GAR subscription needs to be created or
        updated when an action occurred in the Back Office.
        Creating a subscription is done via PUT method.
        Updating a subscription is done via POST method.
        """

        if not self.initial:
            response = self._get_response_from_gar(http_method="PUT")
            if response.status_code not in [201, 200]:
                raise ValidationError(response.text)
        else:
            response = self._get_response_from_gar(http_method="POST")
            if response.status_code != 200:
                raise ValidationError(response.text)

    def _get_response_from_gar(self, http_method):
        url = get_gar_request_url(self.cleaned_data["subscription_id"])
        cert = get_gar_certificate()
        headers = get_gar_headers()
        response = requests.request(
            http_method,
            url,
            data=self._get_gar_data_to_send(http_method=http_method),
            cert=cert,
            headers=headers,
        )

        if response.status_code == 409 and "existe deja" in response.text:
            response = self._get_response_from_gar(http_method="POST")

        return response

    def _get_gar_data_to_send(self, http_method=None):
        """
        This is the data that needs to be sent when creating a subscription (PUT)
        or when updating a subscription (POST).
        When updating a subscription, the uaiEtab child should be removed.
        """
        uai = self.clean_uai()
        project_code = self.cleaned_data.get("project_code")
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <abonnement xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
           <idAbonnement>{subscription_id}</idAbonnement>
           <idDistributeurCom>{distributor_id}</idDistributeurCom>
           <idRessource>{resources_id}</idRessource>
           <typeIdRessource>ark</typeIdRessource>
           <libelleRessource>{organization_name}</libelleRessource>
           <debutValidite>{start_date}</debutValidite>
           <finValidite>{end_date}T00:00:00</finValidite>
           <uaiEtab>{uai}</uaiEtab>
           <categorieAffectation>transferable</categorieAffectation>
           <typeAffectation>INDIV</typeAffectation>
           <nbLicenceGlobale>ILLIMITE</nbLicenceGlobale>
           <publicCible>ELEVE</publicCible>
           <publicCible>ENSEIGNANT</publicCible>
           <publicCible>DOCUMENTALISTE</publicCible>
           <publicCible>AUTRE PERSONNEL</publicCible>
           <codeProjetRessource>{project_code}</codeProjetRessource>
        </abonnement>""".format(
            subscription_id=self.cleaned_data["subscription_id"],
            distributor_id=GAR_DISTRIBUTOR_ID,
            resources_id=GAR_RESOURCES_ID,
            organization_name=GAR_ORGANIZATION_NAME,
            start_date=self._get_gar_start_date(http_method),
            end_date=self.cleaned_data.get("ends_at"),
            uai=uai,
            project_code=project_code,
        )

        if not project_code:
            xml = xml.replace(
                f"<codeProjetRessource>{project_code}</codeProjetRessource>", ""
            )

        if http_method == "POST":
            xml = xml.replace(f"<uaiEtab>{uai}</uaiEtab>", "")

        return xml

    def _get_gar_start_date(self, http_method):
        """
        The start date (debutValidite) is mandatory but cannot be changed when
        updating a subscription. If we try to update the subscription we have to make a
        GET request to retrieve the start date.
        """
        if http_method == "POST":
            uai = self.clean_uai()
            data = """<?xml version="1.0" encoding="UTF-8"?>
            <filtres xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
                  <filtre>
                        <filtreNom>idDistributeurCom</filtreNom>
                        <filtreValeur>{distributor_id}</filtreValeur>
                  </filtre> 
                  <filtre>
                        <filtreNom>uaiEtab</filtreNom>
                        <filtreValeur>{uai}</filtreValeur>
                  </filtre> 
            </filtres>""".format(
                distributor_id=GAR_DISTRIBUTOR_ID, uai=uai
            )
            cert = get_gar_certificate()
            headers = get_gar_headers()
            response = requests.request(
                "GET",
                "https://abonnement.gar.education.fr/abonnements",
                data=data,
                cert=cert,
                headers=headers,
            )
            soup = BeautifulSoup(response.text, "lxml")
            subscriptions = soup.findAll("abonnement")
            for subscription in subscriptions:
                if (
                    subscription.find("idabonnement").text
                    == self.cleaned_data["subscription_id"]
                ):
                    return subscription.find("debutvalidite").text

        return datetime.now().isoformat()
