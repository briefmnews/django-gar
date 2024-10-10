# django-gar
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/) 
[![Django 4.x](https://img.shields.io/badge/django-4.2-blue.svg)](https://docs.djangoproject.com/en/4.2/)
![Python CI](https://github.com/briefmnews/django-gar/workflows/Python%20CI/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/briefmnews/django-gar/branch/master/graph/badge.svg)](https://codecov.io/gh/briefmnews/django-gar)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)  
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)  
Handle CAS login for the french Gestionnaire d'Accès au Ressources (GAR).

## Installation
Install with [pip](https://pip.pypa.io/en/stable/):
```shell
pip install django-gar
```

## Setup
In order to make `django-gar` works, you'll need to follow the steps below.

### Settings
First you need to add the following configuration to your settings:
```python
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',

    'django_gar',
    ...
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'django_gar.middleware.GARMiddleware', # mandatory
    ...
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    
    'django_gar.backends.GARBackend',
    ...
)
```

### Migrations
Next, you need to run the migrations in order to update your database schema.
```shell
python manage.py migrate
```

### Mandatory settings
Here is the list of all the mandatory settings:
```python
GAR_BASE_URL
GAR_BASE_SUBSCRIPTION_URL
GAR_SUBSCRIPTION_PREFIX
GAR_DISTRIBUTOR_ID
GAR_CERTIFICATE_PATH
GAR_KEY_PATH
GAR_RESOURCES_ID
GAR_ORGANIZATION_NAME
```

The optional settings with their default values:
```python
GAR_ACTIVE_USER_REDIRECT (default: "/")
GAR_INACTIVE_USER_REDIRECT (default: "/")
GAR_QUERY_STRING_TRIGGER (default: "sso_id")
```

## Tests
Testing is managed by `pytest`. Required package for testing can be installed with:
```shell
pip install -r test_requirements.txt
```
To run testing locally:
```shell
pytest
```
