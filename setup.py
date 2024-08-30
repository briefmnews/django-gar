from setuptools import setup

from django_gar import __version__

setup(
    name="django-gar",
    version=__version__,
    description="Handle login and ticket validation for french GAR",
    url="https://github.com/briefmnews/django-gar",
    author="Brief.me",
    author_email="tech@brief.me",
    license="GNU GPL v3",
    packages=["django_gar", "django_gar.migrations", "django_gar.signals"],
    python_requires=">=3.7",
    install_requires=[
        "Django>=4.2",
        "python-cas>=1.6.0",
        "lxml>=4.9.4",
        "requests>=2.29.0",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
    zip_safe=False,
)
