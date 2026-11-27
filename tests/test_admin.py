import pytest
import requests
from bs4 import BeautifulSoup

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied

from django_gar.admin import GARInstitutionAdmin
from django_gar.exceptions import DjangoGARException
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

    @pytest.mark.usefixtures("mock_get_gar_subscription_empty")
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

    def test_get_allocations_no_uai(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution.uai = None
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.get_allocations(gar_institution)

        # THEN
        assert response == ""

    @pytest.mark.usefixtures("mock_get_allocations_empty_response")
    def test_get_allocations_with_empty_allocation(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.get_allocations(gar_institution)

        # THEN
        assert "L'établissement n'a pas encore affecté la ressource" in response

    @pytest.mark.usefixtures(
        "mock_get_allocations_response",
        "mock_gar_request_response",
        "mock_gar_institution_list_response",
    )
    def test_get_allocations_with_csv_data(self, user):
        # GIVEN
        gar_institution = user.garinstitution
        gar_institution_admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = gar_institution_admin.get_allocations(gar_institution)

        # THEN
        assert "idAbonnement : briefme_0941295X_1709542737.2902117<br/>" in response
        assert "cumulAffectationEnseignant : 226<br/>" in response

    def test_ends_at_is_readonly_on_change(self, user):
        # GIVEN
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        change_fields = admin.get_readonly_fields(request=None, obj=user.garinstitution)
        add_fields = admin.get_readonly_fields(request=None, obj=None)

        # THEN
        assert "ends_at" in change_fields
        assert "ends_at" not in add_fields

    @pytest.mark.parametrize("has_allocations", [True, False])
    def test_get_deleted_objects_protects_allocated_institution(
        self, user, mocker, rf, admin_user, has_allocations
    ):
        # GIVEN
        mocker.patch.object(
            GARInstitution, "has_allocations", return_value=has_allocations
        )
        request = rf.post("/")
        request.user = admin_user
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        *_, protected = admin.get_deleted_objects([user.garinstitution], request)

        # THEN
        assert bool(protected) is has_allocations

    def _gar_subscriptions_request(self, rf, user, uai=None):
        data = {"uai": uai} if uai is not None else None
        request = rf.post("/", data)
        request.user = user
        request.session = "session"
        request._messages = FallbackStorage(request)
        return request

    def test_gar_subscriptions_displays_all_and_normalizes_uai(
        self, rf, admin_user, mocker
    ):
        # GIVEN
        with open("tests/fixtures/get_gar_subscription_response.xml") as xml_response:
            abonnements = BeautifulSoup(xml_response.read(), "lxml").findAll(
                "abonnement"
            )
        mock_get = mocker.patch(
            "django_gar.admin.get_gar_subscriptions", return_value=abonnements
        )
        request = self._gar_subscriptions_request(rf, admin_user, " 0561622j ")
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = admin.gar_subscriptions(request)

        # THEN
        mock_get.assert_called_once_with("0561622J")
        ids = [
            value
            for fields in response.context_data["subscriptions"]
            for key, value in fields
            if key == "idabonnement"
        ]
        assert ids == ["briefeco_1630592291", "briefme_1630592238"]

    def test_gar_subscriptions_empty(self, rf, admin_user, mocker):
        # GIVEN
        mocker.patch("django_gar.admin.get_gar_subscriptions", return_value=[])
        request = self._gar_subscriptions_request(rf, admin_user, "0561622J")
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = admin.gar_subscriptions(request)

        # THEN
        assert response.context_data["subscriptions"] == []

    @pytest.mark.parametrize(
        "side_effect, needle",
        [
            (DjangoGARException(status_code=503, message="boom"), "503"),
            (requests.Timeout(), "30"),
        ],
    )
    def test_gar_subscriptions_gar_error(
        self, rf, admin_user, mocker, side_effect, needle
    ):
        # GIVEN
        mocker.patch(
            "django_gar.admin.get_gar_subscriptions", side_effect=side_effect
        )
        request = self._gar_subscriptions_request(rf, admin_user, "0561622J")
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN
        response = admin.gar_subscriptions(request)

        # THEN
        assert needle in str(list(get_messages(request))[0])
        assert response.context_data["subscriptions"] is None

    def test_gar_subscriptions_requires_view_permission(self, rf, user):
        # GIVEN
        user.is_staff = True
        request = self._gar_subscriptions_request(rf, user, "0561622J")
        admin = GARInstitutionAdmin(GARInstitution, AdminSite())

        # WHEN / THEN
        with pytest.raises(PermissionDenied):
            admin.gar_subscriptions(request)
