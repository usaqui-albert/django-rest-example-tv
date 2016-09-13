from django.contrib import admin

from .models import Country, State

admin.site.register(State)
admin.site.register(Country)
