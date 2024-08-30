import pytest
import requests

from django_gar.forms import GARInstitutionForm

pytestmark = pytest.mark.django_db


class TestGARInstitutionForm:
    def test_form_works_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            GARInstitutionForm,
            "_get_response_from_gar",
            return_value=response_from_gar(201, "dummy response message"),
        )

        # WHEN
        form = GARInstitutionForm(data=form_data().data)

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_creating_instance(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            GARInstitutionForm,
            "_get_response_from_gar",
            return_value=response_from_gar(400, "dummy error message"),
        )

        # WHEN
        form = GARInstitutionForm(data=form_data().data)

        # THEN
        assert mock_request.called_once()
        assert not form.is_valid()

    def test_form_works_with_gar_when_try_creating_instance_that_already_exists(
        self, form_data, mocker, response_from_gar
    ):
        # GIVEN
        mock_request = mocker.patch.object(
            requests,
            "request",
            side_effect=[
                response_from_gar(409, "Cette abonnement existe deja"),
                response_from_gar(200, "Hello"),
                response_from_gar(201, "OK"),
            ],
        )

        # WHEN
        form = GARInstitutionForm(data=form_data().data)
        form.save()

        # THEN
        assert mock_request.call_count == 3
        assert form.is_valid()

    def test_form_works_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user
    ):
        # GIVEN
        institution = user.garinstitution
        data = form_data(garinstitution=institution).data
        institution.save()
        mock_request = mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, "dummy response message"),
        )

        # WHEN
        form = GARInstitutionForm(instance=institution, data=data)
        form.save()

        # THEN
        assert mock_request.called_once()
        assert form.is_valid()

    def test_form_error_with_gar_when_updating_instance(
        self, form_data, mocker, response_from_gar, user
    ):
        # GIVEN
        institution = user.garinstitution
        data = form_data(garinstitution=institution).data
        institution.save()
        error_message = "dummy error message"
        mock_request = mocker.patch.object(
            requests, "request", return_value=response_from_gar(400, error_message)
        )

        # WHEN
        form = GARInstitutionForm(instance=institution, data=data)

        # THEN
        assert mock_request.called_once()
        assert not form.is_valid()
