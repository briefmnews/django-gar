import pytest
import requests

from django.contrib.admin.sites import AdminSite

from django_gar.admin import GARInstitutionAdmin
from django_gar.models import GARInstitution

pytestmark = pytest.mark.django_db


class TestGARInstitutionAdmin:
    def test_gar_subscription_is_deleted_via_api(self, mocker, request_builder, user):
        # GIVEN
        institution = user.garinstitution
        institution.save()
        request = request_builder.get()
        mock_request = mocker.patch.object(requests, "delete", return_value="OK")

        # WHEN
        institution = GARInstitutionAdmin(GARInstitution, AdminSite()).delete_model(
            request=request, obj=institution
        )

        # THEN
        assert not institution
        assert mock_request.called_once()
