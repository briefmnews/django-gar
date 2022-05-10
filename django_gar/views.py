import logging

from bs4 import BeautifulSoup

from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .models import GARSession

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def post(self, request, *args, **kwargs):
        data = request.body.decode("utf-8")

        logger.info(data)

        soup = BeautifulSoup(data, "xml")
        session_index = soup.find("samlp:SessionIndex")

        if session_index:
            try:
                gar_session = GARSession.objects.get(ticket=session_index.text)
                Session.objects.filter(session_key=gar_session.session_key).delete()
                logger.info(f"deleting GAR session {gar_session.session_key}")
            except GARSession.DoesNotExist:
                logger.info("cannot delete GAR session as it does not exist anymore")

        return HttpResponse(status=204)
