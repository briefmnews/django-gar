from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class GARInstitution(models.Model):
    uai = models.CharField(
        "Unité Administrative Immatriculée", max_length=14, unique=True
    )
    institution_name = models.CharField("Nom de l'institution", max_length=255)
    id_ent = models.CharField("ID de l'ent", max_length=255, null=True)
    ends_at = models.DateField("Date de fin d'abonnement", null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_id = models.CharField("id abonnement", max_length=255, unique=True)
    project_code = models.CharField(
        "Code de projet ressources", max_length=50, null=True, blank=True
    )

    def __str__(self):
        return f"{self.institution_name} ({self.uai})"


class GARSession(models.Model):
    """Store GAR active session. This will help us to delete user sessions when the user log out from the GAR"""

    ticket = models.CharField("CAS ticket", max_length=255, unique=True)
    session_key = models.CharField("Django session key", max_length=255, unique=True)

    def __str__(self):
        return f"ticket: {self.ticket} - session_key: {self.session_key}"
