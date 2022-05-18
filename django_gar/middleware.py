import logging

from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib.auth import login

from cas import CASClient
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from .backends import GARBackend
from .models import GARSession
from .utils import remove_external_links_from_html, remove_external_links_from_json

logger = logging.getLogger(__name__)

GAR_BASE_URL = getattr(settings, "GAR_BASE_URL", "")
GAR_ACTIVE_USER_REDIRECT = getattr(settings, "GAR_ACTIVE_USER_REDIRECT", "/")
GAR_INACTIVE_USER_REDIRECT = getattr(settings, "GAR_INACTIVE_USER_REDIRECT", "/")
GAR_QUERY_STRING_TRIGGER = getattr(settings, "GAR_QUERY_STRING_TRIGGER", "sso_id")
GAR_LOGOUT_URL = getattr(settings, "GAR_LOGOUT_URL", "/")


class GARMiddleware:
    """
    Middleware that allows CAS authentication with GAR
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        uai_number = request.GET.get(GAR_QUERY_STRING_TRIGGER, "")
        cas_ticket = request.GET.get("ticket", "")

        if cas_ticket and request.session.get("is_gar"):
            del request.session["is_gar"]
            uai_numbers = self.validate_ticket(request, cas_ticket)

            user = GARBackend.authenticate(request, uai_numbers=uai_numbers)
            if user:
                login(request, user, backend="django_gar.backends.GARBackend")

                # Session key might not exist at this point.
                # Calling save will force session to create a session_key
                request.session.save()
                GARSession.objects.update_or_create(
                    session_key=request.session.session_key,
                    defaults={"ticket": cas_ticket},
                )

                request.session["gar_user"] = True
                return HttpResponseRedirect(GAR_ACTIVE_USER_REDIRECT)
            else:
                return HttpResponseRedirect(GAR_INACTIVE_USER_REDIRECT)

        elif uai_number and uai_number.upper() == "GAR":
            url = self.get_cas_login_url(request)
            request.session["is_gar"] = True
            return HttpResponseRedirect(url)

        response = self.get_response(request)

        return response

    def get_cas_login_url(self, request):
        """Returns the CAS login url"""

        client = self.get_cas_client(request)

        return client.get_login_url()

    def validate_ticket(self, request, cas_ticket):
        """
        Validate the CAS ticket. Ticket lifetime is around 5 seconds.
        Returns the uai number if the user has access, None otherwise
        """

        client = self.get_cas_client(request)
        response = client.get_verification_response(cas_ticket)

        logger.info(response)

        try:
            tree = ElementTree.fromstring(response)
            ns = {"cas": "http://www.yale.edu/tp/cas"}
            auth_success_element = tree.find("cas:authenticationSuccess", ns)

            auth_success_element = auth_success_element.find("cas:attributes", ns)
            uai_element = "cas:UAI"

            uai_numbers = [
                uai.text.upper()
                for uai in auth_success_element.findall(uai_element, ns)
            ]
            return uai_numbers

        except (AttributeError, ParseError):
            return None

    @staticmethod
    def get_redirect_url(request):
        """Get redirect url for cas"""

        scheme = request.scheme
        host = request.get_host()
        url = "{}://{}/?{}={}".format(scheme, host, GAR_QUERY_STRING_TRIGGER, "gar")

        return url

    def get_cas_client(self, request):
        """Create a CAS client"""
        service_url = self.get_redirect_url(request)

        client = CASClient(version=3, server_url=GAR_BASE_URL, service_url=service_url)

        return client


class GARRemoveExternalLinks:
    """Remove external links from html and json to be GAR compliant"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "gar_user" in request.session and "Content-Type" in response:
            if "text/html" in response["Content-Type"]:
                response.content = remove_external_links_from_html(response.content)
            elif "application/json" in response["Content-Type"]:
                response.content = remove_external_links_from_json(response.content)

        return response


class GARLogoutRedirect:
    """Redirect user to GAR_LOGOUT_URL when logged out from GAR"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.session.get("gar_logout"):
            request.session.delete()
            return HttpResponseRedirect(GAR_LOGOUT_URL)

        return response
