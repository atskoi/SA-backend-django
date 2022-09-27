from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered


# Automatically register all your models here from rrf
app_models = apps.get_app_config('rrf').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass