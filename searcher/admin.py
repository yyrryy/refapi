from django.contrib import admin


# Register your models here.
from . import models
admin.site.register(models.Cars)
admin.site.register(models.Products)
admin.site.register(models.Brand)
admin.site.register(models.Brandpdcts)
admin.site.register(models.Refpdcts)
admin.site.register(models.Carmodel)
admin.site.register(models.Cartarget)
admin.site.register(models.Token)
admin.site.register(models.Config)
admin.site.register(models.Refbrands)
admin.site.register(models.Configuration)
admin.site.register(models.Systemstock)
# admin.site.register(models.Brand)
# admin.site.register(models.Brand)
# admin.site.register(models.Brand)
