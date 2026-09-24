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


ALLOCATIONS_HEADER = (
    "UAI;idAbonnement;codeProjetRessource;idRessource;cumulAffectationEleve;"
    "cumulAffectationEnseignant;cumulAffectationDocumentaliste;"
    "cumulAffectationAutrePersonnel"
)


class TestGARInstitutionHasAllocations:
    @pytest.mark.parametrize(
        "status_code, content, expected",
        [
            (200, f"{ALLOCATIONS_HEADER}\nX;id;null;ark;0;0;2;0", True),
            (200, f"{ALLOCATIONS_HEADER}\nX;id;null;ark;0;0;0;0", False),
            (404, "", False),
            (500, "", True),
        ],
        ids=["allocated", "zero", "unknown_subscription", "gar_error"],
    )
    def test_has_allocations(
        self, user, mocker, response_from_gar, status_code, content, expected
    ):
        # GIVEN
        mocker.patch(
            "django_gar.models.get_allocations",
            return_value=response_from_gar(
                status_code=status_code, content=content.encode()
            ),
        )

        # WHEN
        result = user.garinstitution.has_allocations()

        # THEN
        assert result is expected

    def test_has_allocations_without_subscription_id(self, user, mocker):
        # GIVEN
        mock_get_allocations = mocker.patch("django_gar.models.get_allocations")
        user.garinstitution.subscription_id = ""

        # WHEN
        result = user.garinstitution.has_allocations()

        # THEN
        assert result is False
        mock_get_allocations.assert_not_called()
