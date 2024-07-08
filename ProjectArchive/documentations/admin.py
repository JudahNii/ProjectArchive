from django.contrib import admin
from .models import Programme, Department, Faculty, Documentation, Supervisor

# Register your models here.
for model in [Programme, Department, Faculty, Documentation, Supervisor]:
    admin.site.register(model)
