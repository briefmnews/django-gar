# Generated by Django 2.2.15 on 2020-09-15 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_gar", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="garinstitution",
            name="subscription_id",
            field=models.CharField(
                default="temporary_id", max_length=255, verbose_name="id abonnement"
            ),
            preserve_default=False,
        ),
    ]