# Generated by Django 2.2.28 on 2022-05-10 08:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_gar", "0003_auto_20201001_1054"),
    ]

    operations = [
        migrations.CreateModel(
            name="GARSession",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ticket",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="CAS ticket"
                    ),
                ),
                (
                    "session_key",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Django session key"
                    ),
                ),
            ],
        ),
    ]
