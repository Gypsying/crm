from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from django.contrib.admin.sites import site

class AryaConfig(AppConfig):
    name = 'arya'

    def ready(self):
        autodiscover_modules('arya', register_to=site)
