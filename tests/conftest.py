import datetime
import pytest
import requests

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from .factories import UserFactory, GARSessionFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def user_without_institution():
    user = UserFactory()
    user.garinstitution.delete()
    return user


@pytest.fixture
def gar_session():
    return GARSessionFactory()


@pytest.fixture
def mock_validate_valid_ticket(mocker, user):
    return mocker.patch(
        "django_gar.middleware.GARMiddleware.validate_ticket",
        return_value=[user.garinstitution.uai],
    )


@pytest.fixture
def mock_validate_invalid_ticket(mocker):
    return mocker.patch(
        "django_gar.middleware.GARMiddleware.validate_ticket", return_value=[]
    )


@pytest.fixture
def mock_get_allocations_response(mocker, response_from_gar):
    file = "tests/fixtures/get_allocations_response"
    with open(file, "r") as response:
        return mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(
                status_code=200, content=response.read().encode("utf-8")
            ),
        )


@pytest.fixture
def mock_get_allocations_empty_response(mocker, response_from_gar):
    return mocker.patch.object(
        requests,
        "request",
        return_value=response_from_gar(status_code=200, content=b""),
    )


@pytest.fixture
def mock_get_gar_subscription(mocker, response_from_gar):
    file = "tests/fixtures/get_gar_subscription_response.xml"
    with open(file, "r") as response:
        return mocker.patch.object(
            requests,
            "request",
            return_value=response_from_gar(200, message=response.read()),
        )


@pytest.fixture
def request_builder():
    """Create a request object"""
    return RequestBuilder()


class RequestBuilder:
    @staticmethod
    def get(path="/", user=None):
        rf = RequestFactory()
        request = rf.get(path=path)
        request.user = user or AnonymousUser()

        middleware = SessionMiddleware("dummy")
        middleware.process_request(request)
        request.session.save()

        return request

    @staticmethod
    def post(
        path="/",
        data=None,
    ):
        rf = RequestFactory()
        request = rf.post(
            path=path, data=data, content_type="application/x-www-form-urlencoded"
        )

        return request


@pytest.fixture
def mock_verification_response(mocker):
    file = "tests/fixtures/valid_ticket_gar.xml"

    with open(file, "r") as xml_response:
        return mocker.patch(
            "cas.CASClientV2.get_verification_response",
            return_value=xml_response.read(),
        )


@pytest.fixture(autouse=True)
def mock_get_gar_institution_list(mocker, response_from_gar):
    file = "tests/fixtures/institution_list.xml"

    with open(file, "r") as xml_response:
        return mocker.patch(
            "django_gar.signals.handlers.get_gar_institution_list",
            return_value=response_from_gar(
                status_code=200, content=xml_response.read()
            ),
        )


@pytest.fixture(autouse=True)
def mock_delete_subscription_in_gar(mocker, response_from_gar):
    return mocker.patch(
        "django_gar.signals.handlers.delete_gar_subscription",
        return_value=response_from_gar(status_code=204),
    )


@pytest.fixture
def logout_body():
    file = "tests/fixtures/logout.txt"

    with open(file, "r") as text_response:
        return text_response.read()


@pytest.fixture
def html_content():
    return (
        '<html lang="en"><body><p>Le terme économie vient du grec «&nbsp;oikonomia&nbsp;» '
        "qui signifie «&nbsp;l’administration d’une maison&nbsp;», explique "
        '<a href="https://www.dictionnaire-academie.fr/article/A9E0288?utm_source=briefeco&amp;referrer=briefeco" rel="noopener" target="_blank">l’Académie française sur son site</a>. '
        '«&nbsp;Oikonomia&nbsp;» est <a href="https://www.dummy.io/dummy-url" rel="noopener" target="_blank">lui-même la contraction de deux mots</a> en grec&nbsp;: «&nbsp;oikos&nbsp;», '
        "la maison et «&nbsp;nomos&nbsp;», la loi.</p></body></html>"
    )


@pytest.fixture
def json_content():
    json_content = {
        "rewind": [
            {
                "text": "<p><strong>La société d’envoi de résultats de dépistage du Covid-19 Francetest a reconnu aujourd’hui avoir été touchée par une faille de sécurité</strong>, mais a précisé qu’il « n’existe à ce jour aucun élément qui permet de penser que des informations personnelles de patients ou de pharmaciens aient effectivement fuité ». Une enquête publiée par Mediapart dimanche affirme que plus de 700 000 résultats de tests ont été accessibles sur Internet pendant des mois. L’entreprise déclare avoir « remédié » à la faille.</p>",
                "kicker": "Faille de sécurité",
            },
            {
                "text": "<p>La ministre de la Transformation et de la Fonction publiques, Amélie de Montchalin, a annoncé dans une interview publiée hier soir par Le Parisien que <strong>les agents de la fonction publique pouvaient depuis aujourd’hui télétravailler jusqu’à trois jours par semaine si leurs tâches le permettent</strong>. Les syndicats avaient signé un accord en ce sens en juillet, a confirmé la CGT Services publics à B‌r‌i‌e‌f‌.‌m‌e.</p>",
                "kicker": "Télétravail",
            },
            {
                "link": {
                    "url": "https://www.dummy.io/economie-et-social/le-salaire-minimum-en-europe/",
                    "text": "Lire l’article de Toute l’Europe sur le salaire minimum dans l’UE.",
                    "title": "",
                },
                "text": "<p><strong>Le Premier ministre espagnol, Pedro Sanchez, a annoncé aujourd’hui une « augmentation immédiate » du salaire minimum</strong>, sans en préciser le niveau. En Espagne, le salaire minimum a augmenté à deux reprises depuis 2019. Il s’élève actuellement à 1 108 euros brut contre 858 euros brut en juin 2018, date de l’arrivée du socialiste Pedro Sanchez au poste de chef du gouvernement, selon les chiffres de l’institut européen de statistiques Eurostat.</p>",
                "kicker": "Espagne",
            },
            {
                "link": {
                    "url": "https://www.challenges.fr/salon-du-bourget/a400m-la-revanche-de-l-avion-maudit_658139",
                    "text": "Lire l’article de Challenges publié en 2019 sur la « revanche de l’avion maudit ».",
                    "title": "",
                },
                "text": "<p><strong>Le Kazakhstan a commandé deux avions de transport militaire Airbus A400M</strong>, a annoncé aujourd’hui le constructeur aéronautique européen Airbus. Depuis le lancement effectif du programme en 2003, 174 appareils ont été commandés par huit pays, dont seulement un (la Malaisie) n’est pas partenaire du projet de construction de cet avion. Plus de 100 avions ont été livrés. Aucune commande n’avait été enregistrée depuis 2005.</p>",
                "kicker": "Aviation",
            },
        ]
    }

    return str(json_content)


@pytest.fixture
def response_from_gar():
    """Create a response object from GAR ent"""
    return ResponseBuilder


class ResponseBuilder:
    status_code = None
    text = None
    content = None

    def __init__(self, status_code=None, message=None, content=None):
        self.status_code = status_code
        self.text = message
        self.content = content


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
