import requests

from bs4 import BeautifulSoup

from django.conf import settings


GAR_SUBSCRIPTION_PREFIX = getattr(settings, "GAR_SUBSCRIPTION_PREFIX", "")
GAR_BASE_SUBSCRIPTION_URL = getattr(settings, "GAR_BASE_SUBSCRIPTION_URL", "")

GAR_DISTRIBUTOR_ID = getattr(settings, "GAR_DISTRIBUTOR_ID", "")

GAR_CERTIFICATE_PATH = getattr(settings, "GAR_CERTIFICATE_PATH", "")
GAR_KEY_PATH = getattr(settings, "GAR_KEY_PATH", "")


def delete_gar_subscription(subscription_id):
    url = get_gar_request_url(subscription_id)
    cert = get_gar_certificate()
    headers = get_gar_headers()
    requests.delete(url, cert=cert, headers=headers)


def get_gar_request_url(subscription_id):
    base_url = GAR_BASE_SUBSCRIPTION_URL
    url = "{}{}".format(base_url, subscription_id)
    return url


def get_gar_certificate():
    cert = (GAR_CERTIFICATE_PATH, GAR_KEY_PATH)
    return cert


def get_gar_headers():
    headers = {"Content-Type": "application/xml"}
    return headers


def get_gar_subscription_end_date(uai, subscription_id):
    data = """<?xml version="1.0" encoding="UTF-8"?>
    <filtres xmlns="http://www.atosworldline.com/wsabonnement/v1.0/">
          <filtre>
                <filtreNom>idDistributeurCom</filtreNom>
                <filtreValeur>{distributor_id}</filtreValeur>
          </filtre> 
          <filtre>
                <filtreNom>uaiEtab</filtreNom>
                <filtreValeur>{uai}</filtreValeur>
          </filtre> 
    </filtres>""".format(
        distributor_id=GAR_DISTRIBUTOR_ID, uai=uai
    )
    response = requests.request(
        "GET",
        "{}{}".format(GAR_BASE_SUBSCRIPTION_URL, "abonnements"),
        data=data,
        cert=get_gar_certificate(),
        headers=get_gar_headers(),
    )
    soup = BeautifulSoup(response.text, "lxml")
    subscriptions = soup.findAll("abonnement")
    for subscription in subscriptions:
        if subscription.find("idabonnement").text == subscription_id:
            return subscription.find("finvalidite").text
