import pytest

from django.contrib.admin.sites import AdminSite

from django_gar.admin import GARInstitutionAdmin
from django_gar.models import GARInstitution

pytestmark = pytest.mark.django_db


class TestGARInstitutionAdmin:
    def test_gar_subscription_response_no_uai(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution.uai = None
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.gar_subscription_response(gar_institution)

        # THEN
        assert response == ""

    @pytest.mark.usefixtures("mock_get_gar_subscription")
    def test_gar_subscription_response_no_subscription(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.gar_subscription_response(gar_institution)

        # THEN
        assert response == (
            "L'abonnement n'existe pas dans le GAR. "
            "Vous pouvez le supprimer et en créer un nouveau."
        )

    @pytest.mark.usefixtures("mock_get_gar_subscription")
    def test_gar_subscription_response_with_data(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution.subscription_id = "briefme_1630592238"
        gar_institution.uai = "0561622J"
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.gar_subscription_response(gar_institution)

        # THEN
        assert "idabonnement : briefme_1630592238<br/>" in response
        assert "typeaffectation : INDIV<br/>" in response
