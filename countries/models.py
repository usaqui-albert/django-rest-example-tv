from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countrys"

    def __unicode__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"

    def __unicode__(self):
        return self.name
