import pytest

from django.db import IntegrityError

from .factories import InstitutionFactory

pytestmark = pytest.mark.django_db


class TestGARInstitutionModel(object):
    def test_garinstituion_has_unique_uai_number(self, user):
        uai = user.garinstitution.uai
        with pytest.raises(IntegrityError):
            InstitutionFactory(uai=uai, user=user)

    def test_garinstitution_str(self, user):
        institution = user.garinstitution
        assert str(institution) == "{} ({})".format(
            institution.institution_name, institution.uai
        )

    @pytest.mark.usefixtures(
        "mock_gar_institution_list_response",
        "mock_gar_request_response",
    )
    def test_refresh_id_ent_updates_field(self, user):
        # GIVEN
        institution = user.garinstitution
        institution.uai = "0941295X"
        institution.id_ent = None

        # WHEN
        institution.refresh_id_ent()

        # THEN
        assert institution.id_ent == "123456"
