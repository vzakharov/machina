from django.db import models

from utils.django import define_custom_default_field

EloField = define_custom_default_field(lambda: Eloable, lambda cls: cls.DEFAULT_ELO)

class Eloable(models.Model):

    class Meta:
        abstract = True

    DEFAULT_ELO = 1000.0
    K_FACTOR = 32.0

    elo = EloField()
