import os
from django.db import migrations


def add_google_app(apps,schema_editor):
    Site = apps.get_model("sites","Site")
    SocialApp = apps.get_model("socialaccount","SocialApp")

    # default site (id=1 hota hai by default)
    site, _ = Site.objects.get_or_create(
        id=1,
        defaults = {"domain": "localhost:8000","name": "localhost"}
        )

    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    if client_id and secret:
        app, _ = SocialApp.objects.update_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": client_id,
                "secret": secret,
            },
        )
        app.sites.add(site)

class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
        ("sites", "0002_alter_domain_unique"), 
        ("socialaccount", "0001_initial"),

    ]

    operations = [
        migrations.RunPython(add_google_app)
    ]