from django.contrib import admin

from .models import Country, State
# Register your models here.
admin.site.register(State)
admin.site.register(Country)
