import logging
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from defusedxml import ElementTree as ET

from ..models import GARInstitution
from ..gar import get_gar_institution_list, delete_gar_subscription

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=GARInstitution, dispatch_uid="get_id_ent")
def get_id_ent(sender, instance, **kwargs):
    institution_list = get_gar_institution_list()
    xml_data = institution_list.content

    root = ET.fromstring(xml_data)

    namespace = {"ns": "http://www.atosworldline.com/listEtablissement/v1.0/"}

    id_ent = None
    for etablissement in root.findall("ns:etablissement", namespace):
        uai = etablissement.find("ns:uai", namespace)
        if uai is not None and uai.text == instance.uai:
            # Found the correct UAI, now get the idENT
            id_ent_object = etablissement.find("ns:idENT", namespace)
            id_ent = id_ent_object.text if id_ent_object is not None else None
            continue

    if id_ent:
        instance.id_ent = id_ent
    else:
        logger.info(f"id ent doesn't exist for uai {instance.uai}")


@receiver(post_delete, sender=GARInstitution, dispatch_uid="delete_subscription_in_gar")
def delete_subscription_in_gar(sender, instance, **kwargs):
    delete_gar_subscription(instance.subscription_id)
