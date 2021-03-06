import datetime
import pytest

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from .factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def user_without_institution():
    user = UserFactory()
    user.institution.delete()
    return user


@pytest.fixture
def mock_validate_valid_ticket(mocker, user):
    return mocker.patch(
        "django_gar.middleware.GARMiddleware.validate_ticket",
        return_value="GAR",
    )


@pytest.fixture
def mock_validate_invalid_ticket(mocker):
    return mocker.patch(
        "django_gar.middleware.GARMiddleware.validate_ticket", return_value=[]
    )


@pytest.fixture
def request_builder():
    """Create a request object"""
    return RequestBuilder()


class RequestBuilder(object):
    @staticmethod
    def get(path="?"):
        rf = RequestFactory()
        request = rf.get(path)
        request.user = AnonymousUser()

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        return request


@pytest.fixture
def mock_verification_response(mocker):
    file = "tests/fixtures/valid_ticket_gar.xml"

    with open(file, "r") as xml_response:
        return mocker.patch(
            "cas.CASClientV2.get_verification_response",
            return_value=xml_response.read(),
        )


@pytest.fixture
def response_from_gar():
    """Create a response object from GAR ent"""
    return ResponseBuilder


class ResponseBuilder:
    status_code = None
    text = None

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.text = message


@pytest.fixture
def form_data():
    return FormDataBuilder


class FormDataBuilder:
    garinstitution = None

    def __init__(self, garinstitution=None):
        self.garinstitution = garinstitution

    @property
    def data(self):
        if self.garinstitution:
            form_data = {
                "uai": self.garinstitution.uai,
                "institution_name": self.garinstitution.institution_name,
                "ends_at": self.garinstitution.ends_at,
                "user": self.garinstitution.user.id,
                "subscription_id": self.garinstitution.subscription_id,
            }
        else:
            user = UserFactory()
            user.garinstitution.delete()
            form_data = {
                "uai": "00000f",
                "institution_name": "dummy",
                "ends_at": datetime.datetime.today(),
                "user": user.id,
                "subscription_id": "dummy-id",
            }

        return form_data
