import datetime
import factory

from django.contrib.auth import get_user_model

from django_gar.models import GARInstitution, GARSession


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GARInstitution

    institution_name = factory.Sequence(lambda n: "Lycée {0}".format(n))
    uai = "0561641E"
    ends_at = datetime.datetime.today()
    subscription_id = factory.Sequence(lambda n: "prefix_{0}".format(n))


class GARSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GARSession

    session_key = factory.Sequence(lambda n: f"{n}")
    ticket = "ST-2134567"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: "noel{0}@flantier.com".format(n))
    is_active = True
    garinstitution = factory.RelatedFactory(InstitutionFactory, "user")
