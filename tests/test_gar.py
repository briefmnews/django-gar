import pytest
import requests

from django_gar.gar import get_gar_subscription

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
        with pytest.raises(AssertionError):
            get_gar_subscription(
                user.garinstitution.uai, user.garinstitution.subscription_id
            )

        assert mock_request.call_count == 1
