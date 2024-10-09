import pytest
import requests

from django_gar.exceptions import DjangoGARException
from django_gar.gar import get_gar_subscription, get_allocations, GAR_ALLOCATIONS_URL

pytestmark = pytest.mark.django_db()


class TestGetGarSubscription:
    def test_with_subscription_in_response(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.uai = 0561622j
        user.garinstitution.subscription_id = "briefeco_1630592291"
        user.garinstitution.save()
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(200, xml_response.read()),
            )

        # WHEN
        response = get_gar_subscription(
            user.garinstitution.uai, user.garinstitution.subscription_id
        )

        # THEN
        assert mock_request.call_count == 1
        assert response

    def test_with_wrong_subscription_id(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.uai = 0561622j
        user.garinstitution.save()
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(200, xml_response.read()),
            )

        # WHEN
        response = get_gar_subscription(
            user.garinstitution.uai, user.garinstitution.subscription_id
        )

        # THEN
        assert mock_request.call_count == 1
        assert not response

    def test_with_status_code_not_200(self, user, mocker, response_from_gar):
        # GIVEN
        user.garinstitution.subscription_id = "briefeco_1630592291"
        user.garinstitution.save()
        with open(
            "tests/fixtures/get_gar_subscription_response.xml", "r"
        ) as xml_response:
            mock_request = mocker.patch.object(
                requests,
                "request",
                return_value=response_from_gar(404, xml_response.read()),
            )

        # WHEN / THEN
        with pytest.raises(DjangoGARException):
            get_gar_subscription(
                user.garinstitution.uai, user.garinstitution.subscription_id
            )

        assert mock_request.call_count == 1


class TestGetAllocations:
    def test_get_allocations_no_params(self):
        # GIVEN / WHEN
        with pytest.raises(DjangoGARException) as exc_info:
            get_allocations()

        # THEN
        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.message
            == "At least one of subscription_id or project_code is mandatory"
        )

    def test_get_allocations_both_params(self):
        # GIVEN / WHEN
        with pytest.raises(DjangoGARException) as exc_info:
            get_allocations(subscription_id="123", project_code="ABC")

        # THEN
        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.message
            == "Cannot set subscription_id and project_code at the same time"
        )

    def test_get_allocations_with_subscription_id(
        self, user, mock_get_allocations_response
    ):
        # WHEN
        response = get_allocations(subscription_id=user.garinstitution.subscription_id)

        # THEN
        mock_get_allocations_response.assert_called_once_with(
            "GET",
            f"{GAR_ALLOCATIONS_URL}?idAbonnement={user.garinstitution.subscription_id}",
            cert=("", ""),
        )
        assert response.status_code == 200

    def test_get_allocations_with_project_code(self, mock_get_allocations_response):
        # WHEN
        response = get_allocations(project_code="DUMMY")

        # THEN
        mock_get_allocations_response.assert_called_once_with(
            "GET", f"{GAR_ALLOCATIONS_URL}?codeProjetRessource=DUMMY", cert=("", "")
        )
        assert response.status_code == 200
