SECRET_KEY = "dump-secret-key"

ROOT_URLCONF = "django_gar.urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django_gar",
)

AUTHENTICATION_BACKENDS = ("django_gar.backends.GARBackend",)


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

GAR_BASE_URL = "https://idp-auth.partenaire.test-gar.education.fr/"
GAR_QUERY_STRING_TRIGGER = "sso_id"
GAR_ACTIVE_USER_REDIRECT = "/"
GAR_INACTIVE_USER_REDIRECT = "/inactive/"

USE_TZ = True
