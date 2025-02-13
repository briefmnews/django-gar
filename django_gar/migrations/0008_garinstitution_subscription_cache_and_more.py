# Generated by Django 4.2.19 on 2025-02-13 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_gar", "0007_garinstitution_allocations_cache_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="garinstitution",
            name="subscription_cache",
            field=models.JSONField(blank=True, null=True, verbose_name="Abonnement"),
        ),
        migrations.AddField(
            model_name="garinstitution",
            name="subscription_cache_updated_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Dernière mise à jour du cache abonnement",
            ),
        ),
    ]
